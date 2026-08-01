import assert from "node:assert/strict";
import test from "node:test";
import { handleRequest } from "./worker.mjs";

const accessHeaders={"Cf-Access-Authenticated-User-Email":"owner@example.test","Cf-Access-Jwt-Assertion":"test-assertion"};
const pdfBytes=new Uint8Array([37,80,68,70]);
const spellIndex=JSON.stringify({spells:[{name:"Test Spell",page:42,school:"Evocation",levels:"Sor/Wiz 3",classes:["Sorcerer/Wizard"],spell_levels:[3]}]});
const keys=new Set([
  "Spell Compendium.pdf","Spell Compendium v2.pdf","Player's Handbook II spells.pdf","Planar Handbook Spells.pdf","Book of Exalted Deeds Spells.pdf","Book of Vile Darkness Spells.pdf","Miniatures Handbook Spells.pdf",
]);
const env={ALLOWED_EMAIL:"owner@example.test",PRIVATE_LIBRARY:{async get(key){if(keys.has(key))return{body:pdfBytes,size:pdfBytes.byteLength};if(key.endsWith("-index.json")||key==="spell-compendium-index.json")return{body:spellIndex,size:spellIndex.length};return null}}};

const request=(path)=>new Request("https://library.d20srdhub.com"+path,{headers:accessHeaders});

test("rejects requests without Cloudflare Access identity",async()=>{const response=await handleRequest(new Request("https://library.d20srdhub.com/"),env);assert.equal(response.status,403);assert.equal(response.headers.get("Cache-Control"),"private, no-store")});
test("serves all private books and filter controls",async()=>{const response=await handleRequest(request("/"),env);assert.equal(response.status,200);const html=await response.text();for(const name of ["Spell Compendium v2","Player's Handbook II","Planar Handbook","Book of Exalted Deeds","Book of Vile Darkness","Miniatures Handbook"])assert.match(html,new RegExp(name.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")));for(const id of ["book-filter","school-filter","class-filter","level-filter"])assert.match(html,new RegExp(`id="${id}"`))});
test("serves search code for every source and legacy filter derivation",async()=>{const response=await handleRequest(request("/library.js"),env);assert.equal(response.status,200);const script=await response.text();for(const api of ["/api/spells","/api/spells-v2","/api/players-handbook-ii","/api/planar-handbook","/api/book-of-exalted-deeds","/api/book-of-vile-darkness","/api/miniatures-handbook"])assert.ok(script.includes(api));assert.match(script,/deriveFilters/)});
test("serves a new private index",async()=>{const response=await handleRequest(request("/api/players-handbook-ii"),env);assert.equal(response.status,200);assert.deepEqual(await response.json(),JSON.parse(spellIndex))});
test("streams a new private PDF safely",async()=>{const response=await handleRequest(request("/planar-handbook.pdf"),env);assert.equal(response.status,200);assert.equal(response.headers.get("Content-Type"),"application/pdf");assert.equal(response.headers.get("Content-Disposition"),'inline; filename="Planar-Handbook-Spells.pdf"')});
test("supports HEAD without a response body",async()=>{const response=await handleRequest(new Request("https://library.d20srdhub.com/api/miniatures-handbook",{method:"HEAD",headers:accessHeaders}),env);assert.equal(response.status,200);assert.equal(await response.text(),"")});
test("returns a private 404 for unknown paths",async()=>{const response=await handleRequest(request("/missing"),env);assert.equal(response.status,404);assert.equal(response.headers.get("Cache-Control"),"private, no-store")});
