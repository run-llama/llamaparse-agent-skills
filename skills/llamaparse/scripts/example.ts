#!/usr/bin/env node

import LlamaCloud from "@llamaindex/llama-cloud";
import { readFile, writeFile } from "fs/promises";
import { basename } from "path";

// Define a client
const client = new LlamaCloud({
  apiKey: process.env["LLAMA_CLOUD_API_KEY"], // This is the default and can be omitted
});

async function parseFileText(filePath: string): Promise<string> {
  // 1. Convert the file path into a File object
  const buffer = await readFile(filePath);
  const fileName = basename(filePath);
  const file = new File([buffer], fileName);
  // 2. Upload the file to the cloud
  const fileObj = await client.files.create({
    file: file,
    purpose: "parse",
  });
  // 3. Get the file ID
  const fileId = fileObj.id;
  // 4. Use the file ID to parse the file
  const result = await client.parsing.parse({
    tier: "agentic", // allowed values: fast,cost_effective,agentic,agentic_plus
    version: "latest",
    file_id: fileId,
    // IMPORTANT: always include the `expand` parameter. Allowed: text, markdown, items, text_content_metadata,
    // markdown_content_metadata, items_content_metadata, xlsx_content_metadata,
    // output_pdf_content_metadata, images_content_metadata. Metadata fields include
    // presigned URLs.
    expand: ["text_full"],
  });

  // 5. Retrieve the text result (could be None if there was an error)
  return result.text_full ?? "";
}

async function parseFileMarkdown(filePath: string): Promise<string> {
  // 1. Convert the file path into a File object
  const buffer = await readFile(filePath);
  const fileName = basename(filePath);
  const file = new File([buffer], fileName);
  // 2. Upload the file to the cloud
  const fileObj = await client.files.create({
    file: file,
    purpose: "parse",
  });
  // 3. Get the file ID
  const fileId = fileObj.id;
  // 4. Use the file ID to parse the file
  const result = await client.parsing.parse({
    tier: "agentic", // allowed values: fast,cost_effective,agentic,agentic_plus
    version: "latest",
    file_id: fileId,
    // IMPORTANT: always include the `expand` parameter. Allowed: text, markdown, items, text_content_metadata,
    // markdown_content_metadata, items_content_metadata, xlsx_content_metadata,
    // output_pdf_content_metadata, images_content_metadata. Metadata fields include
    // presigned URLs.
    expand: ["markdown_full"],
  });

  // 5. Retrieve the markdown result (could be None if there was an error)
  return result.markdown_full ?? "";
}

async function parseFileJson(filePath: string): Promise<void> {
  // 1. Convert the file path into a File object
  const buffer = await readFile(filePath);
  const fileName = basename(filePath);
  const file = new File([buffer], fileName);
  // 2. Upload the file to the cloud
  const fileObj = await client.files.create({
    file: file,
    purpose: "parse",
  });
  // 3. Get the file ID
  const fileId = fileObj.id;
  // 4. Use the file ID to parse the file
  const result = await client.parsing.parse({
    tier: "agentic", // allowed values: fast,cost_effective,agentic,agentic_plus
    version: "latest",
    file_id: fileId,
    // IMPORTANT: always include the `expand` parameter. Allowed: text, markdown, items, text_content_metadata,
    // markdown_content_metadata, items_content_metadata, xlsx_content_metadata,
    // output_pdf_content_metadata, images_content_metadata. Metadata fields include
    // presigned URLs.
    expand: ["items"],
  });

  // 5. Retrieve the result as a JSON array of items (could be None if there was an error)
  if (result.items) {
    for (const page of result.items.pages) {
      console.log(JSON.stringify(page));
    }
  }
}

async function parseFileWithOptions(filePath: string): Promise<void> {
  // 1. Convert the file path into a File object
  const buffer = await readFile(filePath);
  const fileName = basename(filePath);
  const file = new File([buffer], fileName);
  // 2. Upload the file to the cloud
  const fileObj = await client.files.create({
    file: file,
    purpose: "parse",
  });
  // 3. Get the file ID
  const fileId = fileObj.id;
  // 4. Use the file ID to parse the file
  const result = await client.parsing.parse({
    tier: "agentic", // allowed values: fast,cost_effective,agentic,agentic_plus
    version: "latest",
    file_id: fileId,
    input_options: {
      presentation: {
        skip_embedded_data: false,
      },
    },
    output_options: {
      images_to_save: ["screenshot"],
      markdown: {
        tables: { output_tables_as_markdown: true },
        annotate_links: true,
      },
    },
    processing_options: {
      specialized_chart_parsing: "agentic",
      ocr_parameters: { languages: ["de", "en"] },
    },
    agentic_options: {
      custom_prompt:
        "Extract text from the provided file and translate it from German to English.",
    },
    // IMPORTANT: always include the `expand` parameter. Allowed: text, markdown, items, text_content_metadata,
    // markdown_content_metadata, items_content_metadata, xlsx_content_metadata,
    // output_pdf_content_metadata, images_content_metadata. Metadata fields include
    // presigned URLs.
    expand: [
      "markdown_full",
      "images_content_metadata",
      "markdown_content_metadata",
    ],
  });
  // 5. Retrieve and save the images from the result (since we requested images)
  if (result.images_content_metadata) {
    for (const image of result.images_content_metadata.images) {
      if (image.presigned_url) {
        const response = await fetch(image.presigned_url, {
          headers: {
            Authorization: `Bearer ${process.env["LLAMA_CLOUD_API_KEY"]}`,
          },
        });
        if (response.ok) {
          const content = await response.bytes();
          await writeFile(image.filename, content);
        }
      }
    }
  }
  // 6. Print the full-text result
  console.log(result.markdown_full ?? "No full content");
}
