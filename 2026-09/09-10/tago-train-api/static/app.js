const $ = id => document.getElementById(id);
async function api(url) {
  const response = await fetch(url);
  const body = await response.json();
  if (!response.ok) throw new Error(`${body.error?.message || '요청 실패'} (${body.error?.kind || response.status}, HTTP ${body.error?.http_status || response.status}, API ${body.error?.api_code || '-'})`);
  return body;
}
function options(select, rows, key, label, placeholder) {
  select.replaceChildren(new Option(placeholder, ''), ...rows.map(row => new Option(row[label], row[key])));
}
for (const side of ['departure', 'arrival']) {
  let generation = 0;
  $(side + '-city').addEventListener('change', async event => {
    const current = ++generation;
    options($(side), [], '', '', '역 선택'); $(side).disabled = true;
    if (!event.target.value) return;
    try {
      const data = await api('/stations?city_code=' + encodeURIComponent(event.target.value));
      if (current !== generation) return;
      options($(side), data.items, 'nodeid', 'nodename', '역 선택'); $(side).disabled = false;
      $('status').textContent = data.items.length ? '출발역과 도착역을 선택하세요.' : '해당 지역에 역이 없습니다.';
    } catch (error) { if (current === generation) $('status').textContent = error.message; }
  });
}
$('date').value = $('date').min = new Intl.DateTimeFormat('sv-SE', {timeZone:'Asia/Seoul'}).format(new Date());
$('search-form').addEventListener('submit', async event => {
  event.preventDefault(); $('submit').disabled = true; $('results').replaceChildren();
  $('status').textContent = '시간표를 조회하는 중입니다.';
  try {
    const params = new URLSearchParams(['departure','arrival','date','start_time','end_time','train_type'].map(id => [id, $(id).value]));
    const data = await api('/search?' + params);
    for (const row of data.items) {
      const tr = document.createElement('tr');
      for (const key of ['train_type','train_number','departure','departure_time','arrival','arrival_time']) {
        const td = document.createElement('td'); td.textContent = row[key]; tr.append(td);
      }
      $('results').append(tr);
    }
    $('status').textContent = data.items.length ? `${data.items.length}개의 열차를 찾았습니다.` : '선택한 조건의 열차가 없습니다.';
  } catch (error) { $('status').textContent = error.message; }
  finally { $('submit').disabled = false; }
});
for (const side of ['departure','arrival']) {
  options($(side + '-city'), [], '', '', '지역 목록 로딩 중…');
  $(side + '-city').disabled = true;
}
Promise.allSettled([api('/cities'), api('/train-types')]).then(([cities, types]) => {
  const errors = [];
  for (const side of ['departure','arrival']) {
    const select = $(side + '-city');
    if (cities.status === 'fulfilled') {
      options(select, cities.value.items, 'citycode', 'cityname', cities.value.items.length ? '지역 선택' : '지역 목록 없음');
      select.disabled = !cities.value.items.length;
    } else {
      options(select, [], '', '', '지역 목록 불러오기 실패');
    }
  }
  if (cities.status === 'rejected') errors.push('지역 목록: ' + cities.reason.message);
  if (types.status === 'fulfilled') options($('train_type'), types.value.items, 'vehiclekndid', 'vehiclekndnm', '전체');
  else errors.push('열차 종류: ' + types.reason.message);
  $('status').textContent = errors.length ? errors.join(' / ') : '지역과 역을 선택하세요.';
});
