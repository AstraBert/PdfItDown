# @cle-does-things/pdfitdown-wasm

Package containing WASM bindings for PdfItDown.

Example usage:

```html
<script type="module">
  import init, {
      convert,
  } from "https://unpkg.com/@cle-does-things/pdfitdown-wasm@4.0.0/pkg/pdfitdown_wasm.js";

  
  await init(
      "https://unpkg.com/@cle-does-things/pdfitdown-wasm@4.0.0/pkg/pdfitdown_wasm_bg.wasm",
  );

  const fileInput = document.querySelector('input');
  fileInput.addEventListener('change', async (e) => {
    const bytes = new Uint8Array(await e.target.files[0].arrayBuffer());
    const result = convert(bytes);
    console.log('output bytes:', result);
  });
</script>

<input type="file" />
```
