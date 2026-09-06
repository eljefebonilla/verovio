// Focused Row18b importer contract. Supply a built module and its toolkit wrapper.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const args=process.argv.slice(2), value=flag=>args[args.indexOf(flag)+1];
for(const flag of ['--module','--wrapper'])assert.ok(args.includes(flag),flag+' is required');
const {VerovioToolkit}=await import(pathToFileURL(value('--wrapper')));
const modulePath=value('--module'),m=await(await import(pathToFileURL(modulePath))).default();
const baseline=args.includes('--expect-baseline');
const definitions={
 'voice-switch':{'v1-switch':{qstamp:.5,layer:'1'},'v2-return':{qstamp:.5,layer:'2'},'next-measure':{qstamp:1}},
 'pitch-alter':{'sharp-voice1':{pitch:68},'natural-voice2':{pitch:67},'natural-octave5':{pitch:79},'explicit-flat':{pitch:66},'explicit-natural':{pitch:67},'same-voice-sharp':{pitch:68},'same-voice-omitted':{pitch:67},'same-voice-explicit':{pitch:68}},
 'cross-staff':{'cross-start':{qstamp:0,pitch:60},'cross-chord':{qstamp:0,pitch:52,staff:'2'},'cross-next':{qstamp:1,pitch:55,staff:'2'}},
 'half-alter':{'half-sharp':{accidGes:'sd'},'half-flat':{accidGes:'fu'},'three-half-sharp':{accidGes:'su'},'three-half-flat':{accidGes:'fd'}}
};
const results=[];let version;
for(const [name,expected]of Object.entries(definitions)){
 const t=new VerovioToolkit(m);version=t.getVersion();t.setOptions({xmlIdChecksum:true,font:'Leland',header:'none',footer:'none'});
 const xml=readFileSync(new URL('../tests/musicxml/row18b/'+name+'.musicxml',import.meta.url),'utf8');assert.equal(t.loadData(xml),1);
 const map=t.renderToTimemap(),mei=t.getMEI();
 const layers=[...mei.matchAll(/<layer\b[^>]*\bn="([^"]+)"[^>]*>([\s\S]*?)<\/layer>/g)];
 if(name==='voice-switch')assert.deepEqual(layers.filter(x=>x[2].includes('<barLine')).map(x=>x[1]),['2'],'unvoiced middle barline retains current layer');const on=Object.fromEntries(map.flatMap(e=>(e.on??[]).map(id=>[id,e.qstamp])));const cases=[];
 for(const [id,want]of Object.entries(expected)){
  const note=mei.match(new RegExp('<note\\b[^>]*xml:id="'+id+'"[^>]*>[\\s\\S]*?<\\/note>'))?.[0]??'';
  const actual={layer:layers.find(x=>x[2].includes('xml:id="'+id+'"'))?.[1],qstamp:on[id],pitch:t.getMIDIValuesForElement(id).pitch,accidGes:note.match(/accid.ges="([^"]+)"/)?.[1],staff:note.match(/\bstaff="([^"]+)"/)?.[1]};
  cases.push({id,want,actual,pass:Object.entries(want).every(([k,v])=>actual[k]===v)});
 }
 results.push({fixture:name,sha256:createHash('sha256').update(xml).digest('hex'),cases});t.destroy();
}
const report={version,moduleSha256:createHash('sha256').update(readFileSync(modulePath)).digest('hex'),expectBaseline:baseline,results};
if(args.includes('--output'))writeFileSync(value('--output'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
if(baseline){for(const name of ['voice-switch','pitch-alter'])assert.ok(results.find(r=>r.fixture===name).cases.some(c=>!c.pass),name+' must fail before patch');assert.ok(results.find(r=>r.fixture==='cross-staff').cases.every(c=>c.pass),'baseline cross-staff fixture must pass');}
else assert.ok(results.every(r=>r.cases.every(c=>c.pass)),'importer contract failed');
