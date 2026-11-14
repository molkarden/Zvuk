(()=>{
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const ls={g:(k,d)=>{try{const v=JSON.parse(localStorage.getItem(k));return v==null?d:v}catch(e){return d}},s:(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
const goal=n=>{try{if(window.ym&&window.YM_ID)ym(window.YM_ID,'reachGoal',n)}catch(e){}};
const rub=n=>n.toLocaleString('ru-RU')+'\u00a0₽';
const toast=t=>{const e=document.createElement('div');e.className='toast';e.setAttribute('role','status');e.textContent=t;document.body.append(e);setTimeout(()=>e.remove(),3200)};
$('.bg')?.addEventListener('click',e=>{const o=document.body.classList.toggle('nav-open');e.currentTarget.setAttribute('aria-expanded',o)});
$$('.sub').forEach(b=>b.addEventListener('click',()=>{const l=b.parentElement;l.classList.toggle('open');b.setAttribute('aria-expanded',l.classList.contains('open'))}));
$$('[data-goal]').forEach(a=>a.addEventListener('click',()=>goal(a.dataset.goal)));
/* cookie */
if(!ls.g('ck',0)){const c=$('#ck');if(c){c.hidden=false;$('button',c).onclick=()=>{ls.s('ck',1);c.hidden=true}}}
/* filters */
const fl=$('#flt');
if(fl){
 const grid=$('#grid'),cards=$$('.card',grid),cnt=$('#cnt'),empty=$('#empty'),ld=$('#ld');
 const sp=new URLSearchParams(location.search);['q','city','genre'].forEach(k=>{const el=fl.elements[k];if(el&&sp.get(k))el.value=sp.get(k)});
 const now=new Date();now.setHours(0,0,0,0);
 const inR=(d,p)=>{const t=new Date(d+'T00:00:00'),df=Math.round((t-now)/864e5),w=t.getDay();
  if(df<0)return false;if(p==='today')return df===0;if(p==='tomorrow')return df===1;
  if(p==='weekend')return df<=7&&(w===0||w===6);
  if(p==='month')return t.getMonth()===now.getMonth()&&t.getFullYear()===now.getFullYear();return true};
 const apply=()=>{const f=new FormData(fl),q=(f.get('q')||'').toLowerCase().trim(),c=f.get('city'),g=f.get('genre'),v=f.get('vt'),mx=+f.get('price')||0,p=f.get('when')||'all';let n=0;
  cards.forEach(el=>{const d=el.dataset,ok=(!q||d.t.includes(q))&&(!c||d.c===c)&&(!g||d.g===g)&&(!v||d.v===v)&&(!mx||+d.p<=mx)&&inR(d.d,p);el.hidden=!ok;if(ok)n++});
  cnt.textContent=n?'Найдено концертов: '+n:'Ничего не найдено';empty.hidden=n>0;ld.hidden=true;grid.setAttribute('aria-busy','false');goal('filter')};
 let tm;const run=()=>{ld.hidden=false;grid.setAttribute('aria-busy','true');cnt.textContent='';clearTimeout(tm);tm=setTimeout(apply,350)};
 fl.addEventListener('input',run);fl.addEventListener('submit',e=>{e.preventDefault();run()});fl.addEventListener('reset',()=>setTimeout(run));
 $('#rst')?.addEventListener('click',()=>{fl.reset()});apply();
}
/* ticket widget */
const tw=$('#tw');
if(tw){
 const base=+tw.dataset.price,cat=$('#cat'),q=$('#qty'),pr=$('#promo'),tot=$('#tot'),unit=$('#unit'),pm=$('#pmsg'),co=$('#co');let disc=0;
 const calc=()=>{const m=+(cat.selectedOptions[0].dataset.m||1),price=Math.round(base*m),n=Math.min(8,Math.max(1,+q.value||1)),t=Math.round(price*n*(1-disc));
  tot.textContent=base?rub(t):'Бесплатно';unit.textContent=base?rub(price)+' × '+n:'Вход по регистрации';return{price,n,t,cat:cat.value}};
 $$('[data-step]',tw).forEach(b=>b.addEventListener('click',()=>{q.value=Math.min(8,Math.max(1,(+q.value||1)+ +b.dataset.step));calc()}));
 cat.addEventListener('change',calc);q.addEventListener('input',calc);
 $('#apply')?.addEventListener('click',()=>{const ok=pr.value.trim().toUpperCase()==='LIVE10';disc=ok?.1:0;pm.textContent=ok?'Промокод применён: −10%':'Такого промокода нет';calc()});
 const open=()=>{const c=calc();$('#sum').textContent=tw.dataset.title+', '+c.cat+', билетов: '+c.n;$('#paysum').textContent=base?rub(c.t):'';co.showModal();goal('checkout_open')};
 $$('[data-buy]').forEach(b=>b.addEventListener('click',open));
 $('[data-close]',co).onclick=()=>co.close();
 $('#cof').addEventListener('submit',e=>{e.preventDefault();const c=calc(),f=new FormData(e.target),id='ZV-'+Date.now().toString(36).toUpperCase();
  const o=ls.g('orders',[]);o.unshift({id,title:tw.dataset.title,date:tw.dataset.date,cat:c.cat,n:c.n,total:c.t,pay:f.get('pay'),name:f.get('name')});ls.s('orders',o);
  e.target.hidden=true;$('#ok').hidden=false;$('#ok h2').textContent='Заказ '+id+' оформлен';goal('order')});
 calc();
}
/* calculator on tickets page */
const kc=$('#kc');
if(kc){const ev=$('#kev'),ct=$('#kct'),qn=$('#kqn'),out=$('#kout');const f=()=>{const p=+ev.selectedOptions[0].dataset.p,m=+ct.value,n=Math.max(1,+qn.value||1);out.textContent=p?rub(Math.round(p*m*n)):'Бесплатно'};kc.addEventListener('input',f);f()}
/* follow */
const fol=ls.g('follow',[]);
$$('[data-follow]').forEach(b=>{const a=b.dataset.follow,set=()=>{const on=ls.g('follow',[]).includes(a);b.setAttribute('aria-pressed',on);b.textContent=on?'♥ Вы подписаны':'♡ Подписаться'};set();
 b.addEventListener('click',()=>{let l=ls.g('follow',[]);const on=l.includes(a);l=on?l.filter(x=>x!==a):[...l,a];ls.s('follow',l);set();toast(on?'Подписка отключена':'Сообщим о новых концертах: '+a);goal('follow')})});
/* forms */
$$('.ajax').forEach(f=>f.addEventListener('submit',e=>{e.preventDefault();const m=ls.g('msgs',[]);m.push({t:f.dataset.type,d:Object.fromEntries(new FormData(f)),ts:Date.now()});ls.s('msgs',m);
 const ok=document.createElement('p');ok.className='ok';ok.setAttribute('role','status');ok.textContent=f.dataset.ok||'Спасибо! Мы ответим в течение рабочего дня.';f.replaceChildren(ok);goal(f.dataset.goal||'form')}));
/* cabinet */
const cab=$('#cab');
if(cab){const au=$('#auth'),pn=$('#panel'),esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 const draw=()=>{const u=ls.g('user',null);au.hidden=!!u;pn.hidden=!u;if(!u)return;$('#uname').textContent=u.name;
  const o=ls.g('orders',[]);$('#orders').innerHTML=o.length?o.map(x=>`<li><b>${esc(x.title)}</b><br><span class="mu">${esc(x.date)}, ${esc(x.cat)}, билетов: ${x.n}, ${x.total?rub(x.total):'бесплатно'}, ${esc(x.pay)}, заказ ${esc(x.id)}</span></li>`).join(''):'<li class="mu">Заказов пока нет. <a href="/afisha/"><u>Выбрать концерт</u></a></li>';
  const fo=ls.g('follow',[]),EV=window.EV||[];$('#follows').innerHTML=fo.length?fo.map(a=>`<li>${esc(a)}</li>`).join(''):'<li class="mu">Подпишитесь на артистов на их страницах, и мы подберём концерты.</li>';
  const gs=new Set(EV.filter(e=>fo.includes(e.a)).map(e=>e.g)),rec=EV.filter(e=>gs.has(e.g)&&!fo.includes(e.a)).slice(0,4);
  $('#recs').innerHTML=rec.length?rec.map(e=>`<li><a href="/koncert/${e.s}/"><u>${esc(e.a)}</u></a> <span class="mu">${esc(e.dt)}, ${esc(e.c)}</span></li>`).join(''):'<li class="mu">Рекомендации появятся после подписки на артистов.</li>'};
 $('#af').addEventListener('submit',e=>{e.preventDefault();const f=new FormData(e.target);ls.s('user',{name:f.get('name'),email:f.get('email')});goal('register');draw()});
 $('#out').onclick=()=>{ls.s('user',null);draw()};draw()}
})();
