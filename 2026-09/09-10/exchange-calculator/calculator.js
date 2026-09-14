(function (root) {
  'use strict';
  function parseCSV(text) {
    const rows = []; let row = [], field = '', quoted = false;
    text = text.replace(/^\uFEFF/, '');
    for (let i = 0; i < text.length; i++) {
      const char = text[i];
      if (char === '"') {
        if (quoted && text[i + 1] === '"') { field += '"'; i++; }
        else quoted = !quoted;
      } else if (char === ',' && !quoted) { row.push(field); field = ''; }
      else if ((char === '\n' || char === '\r') && !quoted) {
        if (char === '\r' && text[i + 1] === '\n') i++;
        row.push(field); if (row.some(value => value.trim())) rows.push(row);
        row = []; field = '';
      } else field += char;
    }
    if (quoted) throw new Error('CSV 따옴표 형식이 올바르지 않습니다.');
    row.push(field); if (row.some(value => value.trim())) rows.push(row);
    return rows;
  }
  function readRates(text) {
    const [headers, ...rows] = parseCSV(text);
    if (!headers || !rows.length) throw new Error('CSV에 환율 자료가 없습니다.');
    const fields = ['date', 'base', 'currency', 'rate'];
    if (fields.some(key => !headers.includes(key))) throw new Error('필수 열: date, base, currency, rate');
    const rates = { USD: 1 }; let date;
    for (const row of rows) {
      if (row.length !== headers.length) throw new Error('CSV 열 개수가 올바르지 않습니다.');
      const item = Object.fromEntries(headers.map((key, i) => [key, row[i]]));
      if (item.base !== 'USD' || !['KRW', 'JPY', 'EUR'].includes(item.currency)) throw new Error('USD 기준의 KRW, JPY, EUR 자료를 선택하세요.');
      if (!/^\d{4}-\d{2}-\d{2}$/.test(item.date) || !Number.isFinite(Date.parse(item.date)) || (date && date !== item.date)) throw new Error('환율 기준일이 올바르지 않거나 서로 다릅니다.');
      if (rates[item.currency] !== undefined) throw new Error('중복된 통화가 있습니다.');
      const rate = Number(item.rate);
      if (!Number.isFinite(rate) || rate <= 0) throw new Error('환율은 0보다 큰 숫자여야 합니다.');
      date = item.date; rates[item.currency] = rate;
    }
    if (['KRW', 'JPY', 'EUR'].some(code => !rates[code])) throw new Error('KRW, JPY, EUR 자료가 모두 필요합니다.');
    return { date, rates };
  }
  function convert(amount, from, to, rates) {
    if (!Number.isFinite(amount) || amount < 0) throw new Error('0 이상의 금액을 입력하세요.');
    if (!rates[from] || !rates[to]) throw new Error('지원하지 않는 통화입니다.');
    const result = amount / rates[from] * rates[to];
    if (!Number.isFinite(result)) throw new Error('금액이 너무 큽니다.');
    return result;
  }
  const api = { parseCSV, readRates, convert };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.Exchange = api;
})(globalThis);
