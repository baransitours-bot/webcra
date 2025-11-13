// Simple viewer: fetch data and populate UI
(async function(){
  const DATA_URL = 'data/crawled_pages.json';
  const listEl = document.getElementById('list');
  const searchEl = document.getElementById('search');
  const countryFilter = document.getElementById('countryFilter');
  const tagFilter = document.getElementById('tagFilter');

  const detailTitle = document.getElementById('detailTitle');
  const metaInfo = document.getElementById('metaInfo');
  const openUrl = document.getElementById('openUrl');
  const textPre = document.getElementById('textPre');
  const htmlFrame = document.getElementById('htmlFrame');
  const contentText = document.getElementById('contentText');
  const contentHtml = document.getElementById('contentHtml');
  const btnText = document.getElementById('showText');
  const btnHtml = document.getElementById('showHtml');

  let data = [];
  try {
    const res = await fetch(DATA_URL);
    data = await res.json();
  } catch (e) {
    listEl.innerHTML = '<li style="color:red">Failed to load data. Start a local server and ensure data/crawled_pages.json exists.</li>';
    console.error(e);
    return;
  }

  // normalize: ensure each item has fields we use
  data = data.map((it, idx) => ({ __idx: idx, url:'', title:'', source:'', country:'', tags:[], timestamp:'', content_text:'', content_html:'', ...it }));

  function renderList(items){
    listEl.innerHTML = '';
    if(!items.length){ listEl.innerHTML = '<li>No results</li>'; return; }
    for(const it of items){
      const li = document.createElement('li');
      li.dataset.idx = it.__idx;
      const t = document.createElement('div'); t.className='title'; t.textContent = it.title || it.url || '(no title)';
      const m = document.createElement('div'); m.className='meta';
      m.textContent = `${it.source||'unknown'} • ${it.country||'N/A'} • ${it.timestamp||''} ${it.tags && it.tags.length ? ' • tags: '+it.tags.join(', ') : ''}`;
      li.appendChild(t); li.appendChild(m);
      li.addEventListener('click', ()=> showDetail(it));
      listEl.appendChild(li);
    }
  }

  function showDetail(it){
    detailTitle.textContent = it.title || it.url || '(no title)';
    metaInfo.innerHTML = `
      <div><strong>URL:</strong> <a href="${it.url||'#'}" target="_blank">${it.url||'—'}</a></div>
      <div><strong>Source:</strong> ${it.source||'—'}</div>
      <div><strong>Country:</strong> ${it.country||'—'}</div>
      <div><strong>Language:</strong> ${it.language||'—'}</div>
      <div><strong>Tags:</strong> ${(it.tags||[]).join(', ')}</div>
      <div><strong>Timestamp:</strong> ${it.timestamp||'—'}</div>
    `;
    openUrl.href = it.url || '#';
    // text
    textPre.textContent = it.content_text || '(no text)';
    // html: use srcdoc for safe local preview
    if(it.content_html){
      try {
        htmlFrame.srcdoc = it.content_html;
      } catch(e){
        htmlFrame.src = 'about:blank';
      }
    } else {
      htmlFrame.srcdoc = '<body><pre>(no html)</pre></body>';
    }
    // default view
    showTextView();
  }

  function showTextView(){ contentHtml.style.display='none'; contentText.style.display='block'; }
  function showHtmlView(){ contentText.style.display='none'; contentHtml.style.display='block'; }

  btnText.addEventListener('click', showTextView);
  btnHtml.addEventListener('click', showHtmlView);

  // filters
  function uniqueValues(arr, key){
    return [...new Set(arr.map(x=> (x && x[key]) || '').filter(Boolean))].sort();
  }
  function populateFilters(){
    const countries = uniqueValues(data,'country');
    countries.forEach(c=> countryFilter.appendChild(Object.assign(document.createElement('option'),{value:c,textContent:c})));
    const tags = [...new Set(data.flatMap(d => d.tags || []))].sort();
    tags.forEach(t=> tagFilter.appendChild(Object.assign(document.createElement('option'),{value:t,textContent:t})));
  }

  function applyFilters(){
    const q = (searchEl.value||'').toLowerCase().trim();
    const c = countryFilter.value;
    const tg = tagFilter.value;
    const filtered = data.filter(item=>{
      if(c && (item.country||'') !== c) return false;
      if(tg && !(item.tags||[]).includes(tg)) return false;
      if(!q) return true;
      const hay = ((item.title||'')+' '+(item.url||'')+' '+(item.source||'')+' '+(item.content_text||'')+' '+((item.tags||[]).join(' '))).toLowerCase();
      return hay.includes(q);
    });
    renderList(filtered);
  }

  // events
  searchEl.addEventListener('input', debounce(applyFilters,200));
  countryFilter.addEventListener('change', applyFilters);
  tagFilter.addEventListener('change', applyFilters);

  populateFilters();
  renderList(data);

  // helpers
  function debounce(fn,ms){
    let t;
    return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a), ms); };
  }

  // If first item exists show
  if(data.length) showDetail(data[0]);

})();
