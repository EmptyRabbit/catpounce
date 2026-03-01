class PageDrawing():
    def __init__(self, page):
        self.page = page

    async def clear_box(self):
        await  self.page.evaluate("""
              () => {
                  const overlays = [
                      'coordinate-box-overlay'
                  ];

                  overlays.forEach(id => {
                      const element = document.getElementById(id);
                      if (element) element.remove();
                  });
              }
          """)

    async def draw_box(self, bbox, color="red", width=1):
        min_x, min_y, max_x, max_y = bbox
        box_width = max_x - min_x
        box_height = max_y - min_y

        await self.page.evaluate(f"""
            () => {{
                // 创建或获取canvas
                let canvas = document.getElementById('coordinate-box-overlay');
                if (!canvas) {{
                    canvas = document.createElement('canvas');
                    canvas.id = 'coordinate-box-overlay';
                    canvas.style.position = 'fixed';
                    canvas.style.top = '0';
                    canvas.style.left = '0';
                    canvas.style.width = '100%';
                    canvas.style.height = '100%';
                    canvas.style.pointerEvents = 'none';
                    canvas.style.zIndex = '9999';
                    canvas.width = window.innerWidth;
                    canvas.height = window.innerHeight;
                    document.body.appendChild(canvas);
                }}

                const ctx = canvas.getContext('2d');
                ctx.strokeStyle = '{color}';
                ctx.lineWidth = {width};

                // 绘制矩形框
                ctx.strokeRect({min_x}, {min_y}, {box_width}, {box_height});
            }}
        """)
