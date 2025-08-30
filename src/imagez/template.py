HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Image Processor</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            ink: "#0b1020",
            panel: "#131a2a",
            edge: "#1b2440",
            primary: { 500:"#6a5acd", 600:"#5a47ce", 700:"#4b39c7" },
            accent: { 500:"#4cc9f0" }
          },
          boxShadow: {
            glow: "0 10px 30px rgba(76,201,240,.15)"
          }
        }
      },
      darkMode: "class"
    }
  </script>
</head>
<body class="min-h-screen bg-gradient-to-b from-ink to-edge text-slate-200">
  <div class="max-w-6xl mx-auto p-6">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <span class="w-3 h-3 rounded-full bg-gradient-to-tr from-primary-600 to-accent-500 shadow-[0_0_16px_rgba(90,71,206,.6)]"></span>
        <span class="text-xl font-semibold tracking-wide text-slate-100">Image Processor</span>
      </div>
    </div>

    <div class="rounded-2xl border border-slate-700/40 bg-panel/80 backdrop-blur-md shadow-glow">
      <div class="px-6 py-4 rounded-t-2xl bg-gradient-to-r from-primary-600 to-accent-500 text-white">
        <h3 class="text-lg font-semibold">Process image</h3>
      </div>

      <div class="p-6">
        <form method="post" enctype="multipart/form-data" id="form" class="grid lg:grid-cols-2 gap-6">
          <div>
            <label for="path" class="block text-sm mb-2 text-slate-300">Input image</label>
            <input id="path" name="path" type="file" accept="image/*" required
                   class="file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium
                          file:bg-primary-600 file:text-white hover:file:brightness-110
                          block w-full text-sm rounded-xl bg-edge/60 border border-slate-700/50 text-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-500/40"/>
            <div id="previewWrap" class="mt-4 hidden rounded-xl border border-slate-700/40 bg-edge/60 p-3">
              <img id="preview" alt="Preview"
                   class="block max-w-full h-auto rounded-lg shadow-xl cursor-crosshair select-none"/>
              <div class="mt-3 flex items-center justify-between">
                <p class="text-xs text-slate-400">Click anywhere on the image to pick that color.</p>
                <div class="flex items-center gap-2">
                  <span id="swatch" class="w-9 h-9 rounded-lg border border-white/10 shadow-inner"></span>
                </div>
              </div>
            </div>
            <canvas id="canvas" class="hidden"></canvas>
          </div>

          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="width_cm" class="block text-sm mb-2 text-slate-300">Width (cm)</label>
                <input id="width_cm" name="width_cm" type="number" step="0.1" value="20.0" required
                       class="w-full rounded-xl bg-edge/60 border border-slate-700/50 px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-500/40"/>
              </div>
              <div>
                <label for="height_cm" class="block text-sm mb-2 text-slate-300">Height (cm)</label>
                <input id="height_cm" name="height_cm" type="number" step="0.1" value="25.0" required
                       class="w-full rounded-xl bg-edge/60 border border-slate-700/50 px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-500/40"/>
              </div>
            </div>

            <div>
              <label class="block text-sm mb-2 text-slate-300">Padding color</label>
              <div class="flex gap-2">
                <input id="padding" name="padding" type="color" value="#000000" title="Pick a color"
                       class="h-10 w-16 rounded-lg bg-edge/60 border border-slate-700/50 p-1"/>
                <input id="padding_text" name="padding_text" type="text" value="#000000" placeholder="#RRGGBB or R,G,B"
                       class="flex-1 rounded-xl bg-edge/60 border border-slate-700/50 px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-500/40"/>
              </div>
            </div>

            <div>
              <label for="dpi" class="block text-sm mb-2 text-slate-300">DPI</label>
              <input id="dpi" name="dpi" type="number" value="300" required
                     class="w-full rounded-xl bg-edge/60 border border-slate-700/50 px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-500/40"/>
            </div>

            <div>
              <label for="mode" class="block text-sm mb-2 text-slate-300">Mode</label>
              <select id="mode" name="mode"
                      class="w-full rounded-xl bg-edge/60 border border-slate-700/50 px-3 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-500/40">
                <option value="todo" selected>todo</option>
                <option value="pdf">pdf</option>
                <option value="image">image</option>
                <option value="image_a4">image_a4</option>
              </select>
            </div>

            <div class="flex flex-wrap gap-3">
              <button type="submit"
                      class="inline-flex items-center justify-center px-5 py-2.5 rounded-xl bg-gradient-to-r from-primary-600 to-primary-700 text-white font-medium shadow-glow hover:brightness-110">
                Process image
              </button>
              <button type="reset"
                      class="inline-flex items-center justify-center px-5 py-2.5 rounded-xl border border-slate-700/50 bg-edge/50 text-slate-200 hover:bg-edge/70">
                Reset
              </button>
            </div>
          </div>
        </form>

        {% if downloads %}
        <div class="mt-6">
          <h5 class="text-slate-100 font-semibold mb-3">Downloads</h5>
          <ul class="space-y-2">
            {% for label, link in downloads %}
            <li class="flex items-center justify-between rounded-lg border border-slate-700/40 bg-edge/60 px-4 py-2">
              <a href="{{ link }}" class="text-primary-500 hover:text-primary-600 underline underline-offset-2">{{ label }}</a>
              <span class="text-xs px-2 py-1 rounded-md bg-slate-200/10 text-slate-300">ready</span>
            </li>
            {% endfor %}
          </ul>
        </div>
        {% endif %}
      </div>
    </div>
  </div>

  <script>
    const clamp=(n,min,max)=>Math.max(min,Math.min(max,n));
    const rgbToHex=(r,g,b)=>["#",
      r.toString(16).padStart(2,"0"),
      g.toString(16).padStart(2,"0"),
      b.toString(16).padStart(2,"0")
    ].join("").toUpperCase();

    const fileInput=document.getElementById("path");
    const preview=document.getElementById("preview");
    const previewWrap=document.getElementById("previewWrap");
    const canvas=document.getElementById("canvas");
    const ctx=canvas.getContext("2d",{willReadFrequently:true});
    const colorPicker=document.getElementById("padding");
    const colorText=document.getElementById("padding_text");
    const swatch=document.getElementById("swatch");

    const setColor=(hex)=>{ colorPicker.value=hex; colorText.value=hex; swatch.style.background=hex; };

    colorPicker.addEventListener("input",()=>setColor(colorPicker.value));
    colorText.addEventListener("input",()=>{
      const v=colorText.value.trim();
      if(/^#[0-9A-F]{6}$/i.test(v)) setColor(v.toUpperCase());
      else if(/^\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*$/.test(v)){
        const [r,g,b]=v.split(",").map(x=>clamp(parseInt(x,10)||0,0,255));
        setColor(rgbToHex(r,g,b));
      }
    });

    fileInput.addEventListener("change",(e)=>{
      const file=e.target.files?.[0]; if(!file) return;
      const reader=new FileReader();
      reader.onload=(ev)=>{
        preview.src=ev.target.result;
        preview.onload=()=>{
          previewWrap.classList.remove("hidden");
          canvas.width=preview.naturalWidth;
          canvas.height=preview.naturalHeight;
          ctx.drawImage(preview,0,0,canvas.width,canvas.height);
        };
      };
      reader.readAsDataURL(file);
    });

    preview.addEventListener("click",(ev)=>{
      if(!preview.src) return;
      const rect=preview.getBoundingClientRect();
      const scaleX=canvas.width/preview.clientWidth;
      const scaleY=canvas.height/preview.clientHeight;
      const x=Math.floor((ev.clientX-rect.left)*scaleX);
      const y=Math.floor((ev.clientY-rect.top)*scaleY);
      const d=ctx.getImageData(x,y,1,1).data;
      setColor(rgbToHex(d[0],d[1],d[2]));
    });

    document.getElementById("form").addEventListener("reset",()=>{
      setTimeout(()=>{
        preview.src="";
        previewWrap.classList.add("hidden");
        canvas.width=canvas.height=0;
        swatch.style.background="transparent";
        setColor("#000000");
      },0);
    });
  </script>
</body>
</html>
"""
