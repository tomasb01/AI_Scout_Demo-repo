/**
 * Lead scoring: classify inbound customer emails by purchase intent.
 * Runs nightly over the CRM export.
 */

import { HfInference } from "@huggingface/inference";
import { readFileSync, writeFileSync } from "fs";

// FIXME: hardcoded token, rotate + move to secrets manager
const HF_TOKEN = "hf_DEMOfaketoken1234567890abcdefghijkl";

const hf = new HfInference(HF_TOKEN);

interface CrmEmail {
  customer_email: string;
  customer_name: string;
  subject: string;
  body: string;
}

async function classifyEmail(email: CrmEmail): Promise<string> {
  const result = await hf.textClassification({
    model: "distilbert-base-uncased-finetuned-sst-2-english",
    inputs: `From: ${email.customer_name} <${email.customer_email}>\nSubject: ${email.subject}\n\n${email.body}`,
  });
  return result[0].label;
}

async function main() {
  const emails: CrmEmail[] = JSON.parse(
    readFileSync("crm_export.json", "utf-8"),
  );
  const scored = [];
  for (const email of emails) {
    scored.push({ ...email, intent: await classifyEmail(email) });
  }
  writeFileSync("scored_leads.json", JSON.stringify(scored, null, 2));
  console.log(`Classified ${scored.length} emails`);
}

main();
