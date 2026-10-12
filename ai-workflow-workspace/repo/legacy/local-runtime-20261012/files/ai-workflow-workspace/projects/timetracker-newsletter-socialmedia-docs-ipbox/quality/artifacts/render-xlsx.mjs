import fs from 'node:fs/promises';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
const directory = new URL('.', import.meta.url);
const book = await SpreadsheetFile.importXlsx(await FileBlob.load(new URL('sample-tracker.xlsx', directory).pathname));
console.log((await book.inspect({kind:'workbook,sheet,table',maxChars:3000,tableMaxRows:4,tableMaxCols:6})).ndjson);
for (const name of ['Summary','Work Entries','Sessions','Manual Inputs','Conflicts','Import Receipts','Metadata']) {
  const end = {'Summary':'B8','Work Entries':'L3','Sessions':'D3','Manual Inputs':'Q3','Conflicts':'C3','Import Receipts':'E3','Metadata':'B7'}[name];
  const image = await book.render({sheetName:name,range:`A1:${end}`,scale:1,format:'png'});
  await fs.writeFile(new URL(name.toLowerCase().replaceAll(' ','-')+'.png',directory),new Uint8Array(await image.arrayBuffer()));
}
console.log((await book.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},summary:'Formula error scan'})).ndjson);
