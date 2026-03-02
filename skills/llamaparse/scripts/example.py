#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#    "llama-cloud>=1.0.0",
#    "httpx>=0.28",
# ]
# ///

import os

import httpx
from llama_cloud import AsyncLlamaCloud


async def parse_file_text(file_path: str) -> str:
    # 1. Define a client
    client = AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
    # 2. Upload the file to the cloud
    file_obj = await client.files.create(
        file=file_path,
        purpose="parse",  # IMPORTANT: always need to specify the purpose.
    )
    # 3. Get the file ID
    file_id = file_obj.id
    # 4. Use the file ID to parse the file
    result = await client.parsing.parse(
        tier="agentic",  # allowed values: fast,cost_effective,agentic,agentic_plus
        version="latest",
        file_id=file_id,
        # IMPORTANT: always include the `expand` parameter. Allowed: text, markdown, items, text_content_metadata,
        # markdown_content_metadata, items_content_metadata, xlsx_content_metadata,
        # output_pdf_content_metadata, images_content_metadata. Metadata fields include
        # presigned URLs.
        expand=["text"],
    )
    # 5. Retrieve the text result (could be None if there was an error)
    return result.text_full or ""


async def parse_file_markdown(file_path: str) -> str:
    # 1. Define a client
    client = AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
    # 2. Upload the file to the cloud
    file_obj = await client.files.create(
        file=file_path,
        purpose="parse",  # IMPORTANT: always need to specify the purpose.
    )
    # 3. Get the file ID
    file_id = file_obj.id
    # 4. Use the file ID to parse the file
    result = await client.parsing.parse(
        tier="agentic",  # allowed values: fast,cost_effective,agentic,agentic_plus
        version="latest",
        file_id=file_id,
        # IMPORTANT: always include the `expand` parameter. Allowed: text, markdown, items, text_content_metadata,
        # markdown_content_metadata, items_content_metadata, xlsx_content_metadata,
        # output_pdf_content_metadata, images_content_metadata. Metadata fields include
        # presigned URLs.
        expand=["markdown"],
    )
    # 5. Retrieve the result (could be None if there was an error)
    return result.markdown_full or ""


async def parse_file_json(file_path: str) -> None:
    # 1. Define a client
    client = AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
    # 2. Upload the file to the cloud
    file_obj = await client.files.create(
        file=file_path,
        purpose="parse",  # IMPORTANT: always need to specify the purpose.
    )
    # 3. Get the file ID
    file_id = file_obj.id
    # 4. Use the file ID to parse the file
    result = await client.parsing.parse(
        tier="agentic",  # allowed values: fast,cost_effective,agentic,agentic_plus
        version="latest",
        file_id=file_id,
        # IMPORTANT: always include the `expand` parameter. Allowed: text, markdown, items, text_content_metadata,
        # markdown_content_metadata, items_content_metadata, xlsx_content_metadata,
        # output_pdf_content_metadata, images_content_metadata. Metadata fields include
        # presigned URLs.
        expand=["items"],
    )
    # 5. Retrieve the result as a JSON array of pages (could be None if there was an error)
    if result.items is not None:
        for page in result.items.pages:
            print(page.model_dump_json(indent=2))


async def parse_file_options(file_path: str) -> None:
    # 1. Define a client
    client = AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
    # 2. Upload the file to the cloud
    file_obj = await client.files.create(
        file=file_path,
        purpose="parse",  # IMPORTANT: always need to specify the purpose.
    )
    # 3. Get the file ID
    file_id = file_obj.id
    # 4. Use the file ID to parse the file.
    # Here we specify several different options.
    # For a complete list of available options, visit: https://developers.llamaindex.ai/python/cloud/llamaparse/api-v2-guide/
    result = await client.parsing.parse(
        tier="agentic",  # allowed values: fast,cost_effective,agentic,agentic_plus
        version="latest",
        file_id=file_id,
        input_options={
            "presentation": {
                "skip_embedded_data": False,
            },
        },
        output_options={
            "images_to_save": ["screenshot"],
            "markdown": {
                "tables": {"output_tables_as_markdown": True},
                "annotate_links": True,
            },
        },
        processing_options={
            "specialized_chart_parsing": "agentic",
            "ocr_parameters": {"languages": ["de", "en"]},
        },
        agentic_options={
            "custom_prompt": "Extract text from the provided file and translate it from German to English."
        },
        # IMPORTANT: always include the `expand` parameter. Allowed: text, markdown, items, text_content_metadata,
        # markdown_content_metadata, items_content_metadata, xlsx_content_metadata,
        # output_pdf_content_metadata, images_content_metadata. Metadata fields include
        # presigned URLs.
        expand=["markdown", "images_content_metadata", "markdown_content_metadata"],
    )
    # 5. Retrieve and save the images from the result (since we requested images)
    if result.images_content_metadata is not None:
        for image in result.images_content_metadata.images:
            if image.presigned_url:
                async with httpx.AsyncClient(
                    headers={
                        "Authorization": f"Bearer {os.getenv('LLAMA_CLOUD_API_KEY')}"
                    }
                ) as client:
                    response = await client.get(image.presigned_url)
                    response.raise_for_status()
                    with open(image.filename, "wb") as f:
                        f.write(response.content)
    # 6. Print the full-text result
    print(result.markdown_full or "No full text result")
