const $ = (selector) => document.querySelector(selector);
const money = (value) => Number(value).toLocaleString('ko-KR', {maximumFractionDigits: 2}) + '원';
let products = [], page = 0, editingId = null, stockId = null, historyId = null;
let loadSequence = 0;

async function api(path, options = {}) {
  const response = await fetch('/api' + path, {
    ...options, headers: {'Content-Type': 'application/json', ...options.headers}
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = Array.isArray(data.detail)
      ? data.detail.map(item => `${item.loc.at(-1)}: ${item.msg}`).join(', ')
      : data.detail;
    throw new Error(detail || '요청에 실패했습니다.');
  }
  return response.status === 204 ? null : response.json();
}

function notice(message, error = false) {
  $('#notice').textContent = message;
  $('#notice').classList.toggle('error', error);
}

function cell(row, value) {
  const td = document.createElement('td');
  td.textContent = value;
  row.append(td);
  return td;
}

function empty(tbody, columns, text) {
  const tr = document.createElement('tr');
  const td = cell(tr, text);
  td.colSpan = columns; td.className = 'empty'; tbody.append(tr);
}

async function load() {
  const sequence = ++loadSequence;
  try {
    const params = new URLSearchParams({q: $('#search').value.trim(),
      low_stock: $('#low-only').checked, limit: 20, offset: page * 20});
    const [rows, summary] = await Promise.all([api('/products?' + params), api('/summary')]);
    if (sequence !== loadSequence) return;
    products = rows;
    $('#products-count').textContent = summary.products.toLocaleString('ko-KR');
    $('#units-count').textContent = summary.units.toLocaleString('ko-KR');
    $('#value-count').textContent = money(summary.stock_value);
    $('#low-count').textContent = summary.low_stock;
    const tbody = $('#product-rows'); tbody.replaceChildren();
    for (const product of products) {
      const tr = document.createElement('tr');
      cell(tr, product.product_name); cell(tr, money(product.price));
      cell(tr, product.quantity); cell(tr, product.min_stock);
      const badge = document.createElement('span');
      const low = product.quantity <= product.min_stock;
      badge.className = 'badge' + (low ? ' low' : '');
      badge.textContent = low ? '재고 부족' : '정상';
      cell(tr, '').append(badge);
      const actions = cell(tr, '');
      for (const [action, label] of [['stock','입출고'],['edit','수정'],['history','이력'],['delete','삭제']]) {
        const button = document.createElement('button');
        button.textContent = label; button.dataset.action = action;
        button.dataset.id = product.product_id;
        button.className = action === 'delete' ? 'danger' : 'secondary';
        actions.append(button);
      }
      tbody.append(tr);
    }
    if (!rows.length) empty(tbody, 6, '등록된 상품이 없거나 검색 결과가 없습니다.');
    $('#previous').disabled = page === 0;
    $('#next').disabled = rows.length < 20;
    $('#page-label').textContent = `${page + 1} 페이지`;
    await loadHistory();
  } catch (error) { notice(error.message, true); }
}

async function loadHistory() {
  const rows = await api('/movements?limit=100' + (historyId ? '&product_id=' + historyId : ''));
  const tbody = $('#history-rows'); tbody.replaceChildren();
  for (const item of rows) {
    const tr = document.createElement('tr');
    cell(tr, item.created_at.replace('T', ' ')); cell(tr, item.product_name);
    cell(tr, item.change_amount > 0 ? '+' + item.change_amount : item.change_amount);
    cell(tr, item.resulting_quantity); cell(tr, item.reason); tbody.append(tr);
  }
  if (!rows.length) empty(tbody, 5, '입출고 이력이 없습니다.');
}

function openProduct(product = null) {
  editingId = product?.product_id ?? null;
  const form = $('#product-form'); form.reset();
  form.querySelector('.form-error').textContent = '';
  $('#product-title').textContent = product ? '상품 수정' : '상품 등록';
  $('#initial-stock-label').hidden = !!product;
  form.elements.quantity.disabled = !!product;
  if (product) {
    for (const name of ['product_name', 'price', 'min_stock']) form.elements[name].value = product[name];
  }
  $('#product-dialog').showModal();
}

$('#new-product').onclick = () => openProduct();
$('#search-form').onsubmit = event => {event.preventDefault(); page = 0; load();};
$('#low-only').onchange = () => {page = 0; load();};
$('#previous').onclick = () => {if (page > 0) {page--; load();}};
$('#next').onclick = () => {page++; load();};
$('#all-history').onclick = async () => {
  historyId = null; $('#history-title').textContent = '최근 입출고';
  try {await loadHistory();} catch (error) {notice(error.message, true);}
};
document.querySelectorAll('[data-close]').forEach(button => {
  button.onclick = () => button.closest('dialog').close();
});

$('#product-rows').onclick = async event => {
  const button = event.target.closest('button[data-action]'); if (!button) return;
  const product = products.find(item => item.product_id === Number(button.dataset.id));
  if (!product) return;
  try {
    switch (button.dataset.action) {
      case 'edit': openProduct(product); break;
      case 'stock': {
        stockId = product.product_id; const form = $('#stock-form'); form.reset();
        form.querySelector('.form-error').textContent = '';
        $('#stock-title').textContent = `${product.product_name} · 재고 ${product.quantity}`;
        $('#stock-dialog').showModal(); break;
      }
      case 'history':
        historyId = product.product_id; $('#history-title').textContent = product.product_name + ' 입출고';
        await loadHistory(); break;
      case 'delete':
        if (!confirm(`'${product.product_name}' 상품을 삭제할까요? 입출고 이력은 보존됩니다.`)) return;
        button.disabled = true;
        await api('/products/' + product.product_id, {method: 'DELETE'});
        notice('상품을 삭제했습니다.'); await load(); break;
    }
  } catch (error) {notice(error.message, true);}
  finally {button.disabled = false;}
};

async function submit(form, path, method, body, message) {
  const button = form.querySelector('[type=submit]'); button.disabled = true;
  form.querySelector('.form-error').textContent = '';
  try {
    await api(path, {method, body: JSON.stringify(body)});
    form.closest('dialog').close(); notice(message); await load();
  } catch (error) {form.querySelector('.form-error').textContent = error.message;}
  finally {button.disabled = false;}
}

$('#product-form').onsubmit = event => {
  event.preventDefault(); const form = event.currentTarget;
  const body = {product_name: form.elements.product_name.value.trim(),
    price: form.elements.price.value, min_stock: Number(form.elements.min_stock.value)};
  if (editingId === null) body.quantity = Number(form.elements.quantity.value);
  submit(form, '/products' + (editingId === null ? '' : '/' + editingId),
    editingId === null ? 'POST' : 'PUT', body, '상품을 저장했습니다.');
};
$('#stock-form').onsubmit = event => {
  event.preventDefault(); const form = event.currentTarget;
  submit(form, '/products/' + stockId + '/stock', 'POST', {
    direction: form.elements.direction.value, quantity: Number(form.elements.quantity.value),
    reason: form.elements.reason.value.trim()
  }, '입출고를 처리했습니다.');
};

load();
