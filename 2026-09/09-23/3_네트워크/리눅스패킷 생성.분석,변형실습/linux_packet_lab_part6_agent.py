import json
import subprocess
from typing import Literal

from agents import Agent, Runner
from agents.decorators import tool


# =========================================================
# 1. 현재 환경 설정
# =========================================================

SERVER_VM = "ubuntu"
CLIENT_VM = "ubuntu1"
SERVER_PORT = 8000

PCAP_FILES = {
    "part4_tcp": "/home/ubuntu/part4_tcp.pcap",
    "part5_compare": "/home/ubuntu/part5_compare.pcap",
}


# =========================================================
# 2. Multipass VM 안에서 Linux 명령을 실행하는 공통 함수
# =========================================================

def run_vm(vm_name: str, command: list[str]) -> dict:
    """
    Windows 호스트에서 multipass exec를 이용해
    지정한 VM 안의 Linux 명령을 실행하고 결과를 dict로 반환한다.
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


# =========================================================
# 3. ubuntu의 IP를 확인하는 내부 보조 함수
# =========================================================

def get_server_ip() -> str:
    result = run_vm(
        SERVER_VM,
        ["hostname", "-I"],
    )

    if result["returncode"] != 0:
        return ""

    addresses = result["stdout"].split()

    if len(addresses) == 0:
        return ""

    return addresses[0]


# =========================================================
# 4. Tool 1 - 기본 IP 연결 확인
# =========================================================

@tool
def ping_test() -> str:
    """
    ubuntu1에서 ubuntu로 ICMP ping을 보내 기본 IP 연결을 확인한다.
    서버까지 기본 네트워크 통신이 되는지 확인해야 할 때 사용한다.
    """

    server_ip = get_server_ip()

    if not server_ip:
        return json.dumps(
            {
                "ok": False,
                "error": "ubuntu의 IP 주소를 확인하지 못했습니다.",
            },
            ensure_ascii=False,
        )

    result = run_vm(
        CLIENT_VM,
        ["ping", "-c", "2", "-W", "2", server_ip],
    )

    result["server_ip"] = server_ip
    result["ping_ok"] = result["returncode"] == 0

    return json.dumps(
        result,
        ensure_ascii=False,
    )


# =========================================================
# 5. Tool 2 - TCP 8000 LISTEN 상태 확인
# =========================================================

@tool
def check_listen_8000() -> str:
    """
    ubuntu에서 TCP 8000번 포트가 LISTEN 상태인지 확인한다.
    ping은 되지만 웹 서비스 연결이 안 되거나 서버 포트를 점검해야 할 때 사용한다.
    """

    result = run_vm(
        SERVER_VM,
        ["ss", "-lnt"],
    )

    result["port"] = SERVER_PORT
    result["listen"] = f":{SERVER_PORT}" in result["stdout"]

    return json.dumps(
        result,
        ensure_ascii=False,
    )


# =========================================================
# 6. Tool 3 - Python HTTP 서버 프로세스 확인
# =========================================================

@tool
def check_http_process() -> str:
    """
    ubuntu에서 Python http.server 프로세스가 실행 중인지 확인한다.
    8000번 LISTEN이 없을 때 서버 프로그램 자체가 실행 중인지 확인하는 데 사용한다.
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


# =========================================================
# 7. Tool 4 - 실제 HTTP 요청 확인
# =========================================================

@tool
def http_test() -> str:
    """
    ubuntu1에서 ubuntu의 TCP 8000번 HTTP 서버로 실제 요청을 보낸다.
    IP 연결과 LISTEN이 정상인 뒤 응용 서비스가 실제로 응답하는지 확인할 때 사용한다.
    """

    server_ip = get_server_ip()

    if not server_ip:
        return json.dumps(
            {
                "ok": False,
                "error": "ubuntu의 IP 주소를 확인하지 못했습니다.",
            },
            ensure_ascii=False,
        )

    url = f"http://{server_ip}:{SERVER_PORT}/"

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
    result["http_ok"] = (
        result["returncode"] == 0
        and "HTTP_CODE=200" in result["stdout"]
    )

    return json.dumps(
        result,
        ensure_ascii=False,
    )


# =========================================================
# 8. Tool 5 - 저장된 pcap 간단 분석
# =========================================================

@tool
def inspect_saved_pcap(
    capture: Literal["part4_tcp", "part5_compare"],
) -> str:
    """
    ubuntu에 저장된 pcap을 tcpdump로 읽어 요약한다.

    Args:
        capture:
            part4_tcp - Part 4의 TCP Handshake pcap
            part5_compare - Part 5의 원본/수정 UDP 비교 pcap
    """

    path = PCAP_FILES[capture]

    result = run_vm(
        SERVER_VM,
        [
            "tcpdump",
            "-nn",
            "-vvv",
            "-X",
            "-c",
            "12",
            "-r",
            path,
        ],
    )

    max_chars = 7000

    if len(result["stdout"]) > max_chars:
        result["stdout"] = (
            result["stdout"][:max_chars]
            + "\n... 출력이 길어 이후 내용은 생략 ..."
        )

    result["capture"] = capture
    result["path"] = path

    return json.dumps(
        result,
        ensure_ascii=False,
    )


# =========================================================
# 9. GPT Agent 정의
# =========================================================

network_agent = Agent(
    name="Linux Network & Packet Diagnostic Agent",

    instructions="""
너는 ubuntu / ubuntu1 Multipass 환경을 점검하는 Linux 네트워크 및 패킷 분석 에이전트다.

환경:
- 서버 VM: ubuntu
- 클라이언트 VM: ubuntu1
- 테스트 HTTP 서비스: TCP 8000
- Part 4 TCP pcap: part4_tcp
- Part 5 원본/수정 비교 pcap: part5_compare

중요 원칙:
1. 사용자의 자연어 질문을 먼저 해석한다.
2. 필요한 경우에만 제공된 Tool을 선택해서 사용한다.
3. Tool의 실제 결과를 확인하지 않고 시스템 상태를 추측하지 않는다.
4. 이미 충분한 정보가 있으면 불필요한 Tool을 반복 호출하지 않는다.
5. 네트워크 장애 질문에서는 IP 연결, LISTEN 포트, 프로세스, 실제 HTTP 요청의 관계를 구분해서 설명한다.
6. pcap 질문에서는 tcpdump 결과를 근거로 Flags, Port, Length, Payload 등 확인 가능한 내용을 설명한다.
7. Tool 결과에 없는 사실은 확인된 사실처럼 말하지 않는다.
8. 임의의 Shell 명령을 만들어 실행할 수 있다고 주장하지 않는다. 사용할 수 있는 것은 등록된 Tool뿐이다.
9. 최종 답변은 한국어로 작성하고, '확인된 사실 → 판단 → 다음 확인/조치' 순서로 간결하게 정리한다.
""",

    tools=[
        ping_test,
        check_listen_8000,
        check_http_process,
        http_test,
        inspect_saved_pcap,
    ],
)


# =========================================================
# 10. 프로그램 시작
# =========================================================

def main() -> None:
    print("=" * 68)
    print(" GPT Linux Network & Packet Diagnostic Agent")
    print("=" * 68)

    question = input("\n문제를 자연어로 입력하세요 > ").strip()

    if not question:
        print("질문이 비어 있습니다.")
        return

    result = Runner.run_sync(
        network_agent,
        question,
    )

    print("\n[Agent 최종 답변]")
    print(result.final_output)

    usage = result.context_wrapper.usage

    print("\n[API 사용량]")
    print("요청 수:", usage.requests)
    print("입력 토큰:", usage.input_tokens)
    print("출력 토큰:", usage.output_tokens)
    print("전체 토큰:", usage.total_tokens)


if __name__ == "__main__":
    main()
