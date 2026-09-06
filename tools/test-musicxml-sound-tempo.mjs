// Row20b mechanism 1 contract; mechanism 2 remains an explicit observation.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const args=process.argv.slice(2),arg=k=>args[args.indexOf(k)+1],sha=b=>createHash('sha256').update(b).digest('hex');
for(const k of ['--module','--wrapper','--output'])assert.ok(args.includes(k),k+' required');
const {VerovioToolkit}=await import(pathToFileURL(arg('--wrapper'))),modulePath=arg('--module'),m=await(await import(pathToFileURL(modulePath))).default();
const baseline=args.includes('--expect-baseline'),out=arg('--output');fs.mkdirSync(out,{recursive:true});
const fixtures=new URL('../tests/musicxml/row20b/',import.meta.url),rows=[];
const counts={'a-no-initial-bare120':[0,1],'b-initial92-bare120':[0,1],'c-exact-choir-bar4-after92':[0,1],'c-first-positional-measure4':[0,0],'control-direction120':[1,1],'d-m92-exact-50-plus120':[2,3],'e-m92-without-later120':[1,2],'f-m92-bare50-only':[0,1],'negative-direction120':[2,2],'negative-mm50':[2,2],'negative-no-tempo':[0,0]};
for(const file of fs.readdirSync(fixtures).filter(f=>f.endsWith('.musicxml')).sort()){
 const name=file.replace('.musicxml',''),xml=fs.readFileSync(new URL(file,fixtures),'utf8');
 if(name.startsWith('negative-'))assert.ok(!xml.replace(/<direction\b[\s\S]*?<\/direction>/g,'').match(/<sound\b[^>]*\btempo=/),'true no-direct-tempo control');
 const t=new VerovioToolkit(m);t.resetXmlIdSeed(1);t.setOptions({breaks:'none'});assert.equal(t.loadData(xml),1);
 const mei=t.getMEI(),headerless=t.getMEI({ignoreHeader:true}),tm=t.renderToTimemap(),tempoTags=[...mei.matchAll(/<tempo\b[^>]*?(?:\/>|>[\s\S]*?<\/tempo>)/g)].map(x=>x[0]);
 assert.equal(tempoTags.length,counts[name][baseline?0:1],name+' tempo object count');
 const tempos=tm.filter(x=>Object.hasOwn(x,'tempo')).map(({qstamp,tempo})=>({qstamp,tempo}));
 if(!baseline){
  if(['b-initial92-bare120','c-exact-choir-bar4-after92'].includes(name))assert.deepEqual(tempos,[{qstamp:0,tempo:92},{qstamp:12,tempo:120}]);
  if(['e-m92-without-later120','f-m92-bare50-only'].includes(name))assert.deepEqual(tempos,[{qstamp:0,tempo:92},{qstamp:4,tempo:50}],'known whole-measure timing remains');
  if(name==='d-m92-exact-50-plus120')assert.deepEqual(tempos,[{qstamp:0,tempo:92},{qstamp:4,tempo:120}],'known last-tempo behavior remains');
  const imported=tempoTags.filter(tag=>/midi.bpm="(?:50|120)"/.test(tag)&&!tag.includes('</tempo>'));
  if(['a-no-initial-bare120','b-initial92-bare120','c-exact-choir-bar4-after92'].includes(name))assert.ok(imported.some(tag=>tag.includes('tstamp="1"')));
  if(name==='f-m92-bare50-only')assert.ok(imported.some(tag=>tag.includes('tstamp="4"')),'actual beat4 retained');
 }
 const files={fullMEI:mei,nativeHeaderlessMEI:headerless,timemap:JSON.stringify(tm,null,2)+'\n'};
 fs.writeFileSync(out+'/'+name+'.svg',t.renderToSVG(1));
 for(const [kind,text]of Object.entries(files))fs.writeFileSync(out+'/'+name+'-'+kind+(kind==='timemap'?'.json':'.mei'),text);
 rows.push({name,version:t.getVersion(),inputSha256:sha(xml),tempoTags,tempos,hashes:Object.fromEntries(Object.entries(files).map(([k,v])=>[k,sha(v)]))});t.destroy();
}
const report={mode:baseline?'baseline':'candidate',moduleSha256:sha(fs.readFileSync(modulePath)),rows,boundary:'Raw native getMEI({ignoreHeader:true}) and raw timemap are available for negative parity. Full MEI retains generated timestamp/version separately. Mechanism2 still applies later tempo to whole measure; conflicting source tempos are unresolved.'};
if(args.includes('--baseline-output')){
 const old=JSON.parse(fs.readFileSync(arg('--baseline-output')+'/report.json','utf8'));report.negativeParity=[];
 for(const r of rows.filter(x=>x.name.startsWith('negative-'))){const b=old.rows.find(x=>x.name===r.name);assert.equal(r.inputSha256,b.inputSha256);for(const kind of ['nativeHeaderlessMEI','timemap']){assert.equal(r.hashes[kind],b.hashes[kind],r.name+' raw '+kind);const suffix=kind==='timemap'?'.json':'.mei';assert.deepEqual(fs.readFileSync(out+'/'+r.name+'-'+kind+suffix),fs.readFileSync(arg('--baseline-output')+'/'+r.name+'-'+kind+suffix));}report.negativeParity.push({name:r.name,rawNativeHeaderlessMEI:true,rawTimemap:true});}
}
fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({mode:report.mode,fixtures:rows.length,negativeParity:report.negativeParity?.length??0,version:rows[0].version}));
