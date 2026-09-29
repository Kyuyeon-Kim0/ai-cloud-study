import asyncio
import json
import subprocess

from agents import Agent, Runner, function_tool


# ---------------------------------------------------------
# 1. 실습 환경 설정
# ---------------------------------------------------------

SERVER_VM = "ubuntu"
CLIENT_VM = "ubuntu1"
PORT = 8000


# ---------------------------------------------------------
# 2. Multipass VM에서 Linux 명령을 실행하는 공통 함수
# ---------------------------------------------------------

def run_vm(vm_name: str, command: list[str]) -> dict:
    """
    Windows에서 multipass exec를 사용해
    지정한 VM 내부의 Linux 명령을 실행한다.
    """

    full_command = [
        "multipass",
        "exec",
        vm_name,
        "--",
    ] + command

    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=10,
        )

        return {
            "vm": vm_name,
            "command": " ".join(command),
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    except subprocess.TimeoutExpired:
        return {
            "vm": vm_name,
            "command": " ".join(command),
            "returncode": -1,
            "stdout": "",
            "stderr": "명령 실행 시간이 10초를 초과했습니다.",
        }


# ---------------------------------------------------------
# 3. 내부 보조 함수: ubuntu의 IP 주소 확인
#    GPT에게 직접 공개하는 도구는 아니다.
# ---------------------------------------------------------

def get_server_ip() -> str:
    result = run_vm(
        SERVER_VM,
        ["hostname", "-I"],
    )

    if result["returncode"] != 0:
        return ""

    addresses = result["stdout"].split()

    if not addresses:
        return ""

    return addresses[0]


# ---------------------------------------------------------
# 4. GPT가 선택해서 사용할 Tool 1: ping
# ---------------------------------------------------------

@function_tool
def ping_test() -> str:
    """
    ubuntu1에서 ubuntu로 ICMP ping을 보내
    기본 IP 네트워크 연결이 가능한지 확인한다.
    네트워크 연결 여부를 먼저 확인해야 할 때 사용한다.
    """

    server_ip = get_server_ip()

    if not server_ip:
        return json.dumps(
            {"error": "ubuntu의 IP 주소를 확인하지 못했습니다."},
            ensure_ascii=False,
        )

    result = run_vm(
        CLIENT_VM,
        ["ping", "-c", "2", "-W", "2", server_ip],
    )

    result["server_ip"] = server_ip

    return json.dumps(
        result,
        ensure_ascii=False,
    )


# ---------------------------------------------------------
# 5. GPT가 선택해서 사용할 Tool 2: 8000 포트
# ---------------------------------------------------------

@function_tool
def check_port_8000() -> str:
    """
    ubuntu에서 TCP 8000번 포트가 LISTEN 상태인지 확인한다.
    ping은 되지만 웹 서비스 접속이 안 될 때 사용한다.
    """

    result = run_vm(
        SERVER_VM,
        ["ss", "-lnt"],
    )

    result["port"] = PORT
    result["listen_8000"] = f":{PORT}" in result["stdout"]

    return json.dumps(
        result,
        ensure_ascii=False,
    )


# ---------------------------------------------------------
# 6. GPT가 선택해서 사용할 Tool 3: HTTP 서버 프로세스
# ---------------------------------------------------------

@function_tool
def check_http_process() -> str:
    """
    ubuntu에서 Python http.server 프로세스가 실행 중인지 확인한다.
    8000번 포트가 열리지 않았을 때 서버 프로그램 실행 여부를 확인하는 데 사용한다.
    """

    result = run_vm(
        SERVER_VM,
        ["pgrep", "-af", "python3 -m http.server"],
    )

    result["process_found"] = result["returncode"] == 0

    return json.dumps(
        result,
        ensure_ascii=False,
    )


# ---------------------------------------------------------
# 7. GPT가 선택해서 사용할 Tool 4: 실제 HTTP 요청
# ---------------------------------------------------------

@function_tool
def http_test() -> str:
    """
    ubuntu1에서 ubuntu의 TCP 8000번 HTTP 서버로 실제 요청을 보내
    응용 서비스가 정상 응답하는지 확인한다.
    """

    server_ip = get_server_ip()

    if not server_ip:
        return json.dumps(
            {"error": "ubuntu의 IP 주소를 확인하지 못했습니다."},
            ensure_ascii=False,
        )

    url = f"http://{server_ip}:{PORT}"

    result = run_vm(
        CLIENT_VM,
        [
            "curl",
            "-sS",
            "-o",
            "/dev/null",
            "-w",
            "HTTP_CODE=%{http_code}",
            "--connect-timeout",
            "3",
            url,
        ],
    )

    result["url"] = url

    return json.dumps(
        result,
        ensure_ascii=False,
    )


# ---------------------------------------------------------
# 8. GPT Agent 만들기
# ---------------------------------------------------------

network_agent = Agent(
    name="Linux Network Diagnostic Agent",

    instructions="""
너는 Multipass 기반 Linux 네트워크 진단 에이전트다.

환경:
- 서버 VM: ubuntu
- 클라이언트 VM: ubuntu1
- 테스트 서비스: TCP 8000번 Python HTTP 서버

사용자의 자연어 문제를 읽고 필요한 도구를 스스로 선택해서 사용하라.

도구의 실제 결과를 확인하지 않고 성공/실패를 추측하지 마라.

일반적인 진단 원칙:
1. 기본 통신 자체가 의심되면 ping_test를 사용한다.
2. ping은 되지만 8000 접속이 안 되면 check_port_8000을 고려한다.
3. 8000 포트가 열려 있지 않다면 check_http_process로 서버 실행 여부를 확인한다.
4. 포트가 열려 있는데 실제 서비스 상태를 확인해야 하면 http_test를 사용한다.
5. 이미 충분한 정보가 있으면 불필요한 도구는 호출하지 않는다.
6. 최종 답변은 한국어로 작성한다.
7. 실행한 도구 결과를 근거로 원인과 다음 확인 방법을 짧고 명확하게 설명한다.
""",

    tools=[
        ping_test,
        check_port_8000,
        check_http_process,
        http_test,
    ],
)


# ---------------------------------------------------------
# 9. 프로그램 시작
# ---------------------------------------------------------

async def main() -> None:
    print("=" * 65)
    print(" GPT Linux Network Diagnostic Agent")
    print("=" * 65)

    question = input("\n문제를 입력하세요 > ")

    result = await Runner.run(
        network_agent,
        question,
    )

    print("\n[GPT Agent 최종 답변]")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
