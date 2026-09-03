import fs from 'fs';
import path from 'path';

function parseCsvRows(csvText: string): string[][] {
  const rows: string[][] = [];
  let currentRow: string[] = [];
  let currentField = '';
  let insideQuotes = false;

  for (let i = 0; i < csvText.length; i++) {
    const char = csvText[i];
    const nextChar = csvText[i + 1];

    if (char === '"') {
      if (insideQuotes && nextChar === '"') {
        currentField += '"';
        i++;
      } else {
        insideQuotes = !insideQuotes;
      }
    } else if (char === ',' && !insideQuotes) {
      currentRow.push(currentField);
      currentField = '';
    } else if ((char === '\n' || char === '\r') && !insideQuotes) {
      if (char === '\r' && nextChar === '\n') {
        i++;
      }
      currentRow.push(currentField);
      if (currentRow.some(f => f.trim().length > 0)) {
        rows.push(currentRow);
      }
      currentRow = [];
      currentField = '';
    } else {
      currentField += char;
    }
  }
  if (currentField || currentRow.length > 0) {
    currentRow.push(currentField);
    rows.push(currentRow);
  }
  return rows;
}

const csvPath = path.resolve(__dirname, '../../ai-service/datasets/processed/oilps_final_master_v2.csv');
const content = fs.readFileSync(csvPath, 'utf-8');
const rows = parseCsvRows(content);

console.log(`Total Master CSV Rows (including header): ${rows.length}`);
const header = rows[0];
const sifIndex = header.indexOf('sif_potential');
console.log(`Header sif_potential Index: ${sifIndex}`);

let trueCount = 0;
let falseCount = 0;

for (let i = 1; i < rows.length; i++) {
  const sifVal = rows[i][sifIndex]?.trim()?.toUpperCase();
  if (sifVal === 'TRUE' || sifVal === '1') {
    trueCount++;
  } else {
    falseCount++;
  }
}

console.log(`Total Records: ${rows.length - 1}`);
console.log(`SIF Potential TRUE Count: ${trueCount}`);
console.log(`SIF Potential Percentage: ${(((trueCount) / (rows.length - 1)) * 100).toFixed(2)}%`);
