import os
import glob
from pathlib import Path
from PIL import Image, ImageOps

def resize_image(image, max_size):
    """Resize image so its longest edge is max_size."""
    width, height = image.size
    if width > max_size or height > max_size:
        if width > height:
            new_width = max_size
            new_height = int(max_size * height / width)
        else:
            new_height = max_size
            new_width = int(max_size * width / height)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return image

def main():
    root_dir = Path(".")
    assets_dir = root_dir / "assets"
    covers_dir = assets_dir / "covers"
    gallery_dir = assets_dir / "gallery"
    projects_dir = root_dir / "projects"
    
    covers_dir.mkdir(parents=True, exist_ok=True)
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    ignore_dirs = {'.git', '.vscode', 'assets', 'projects', '.gemini'}
    
    projects = []
    
    # Process Images
    for d in root_dir.iterdir():
        if d.is_dir() and d.name not in ignore_dirs and not d.name.startswith('.'):
            project_name = d.name
            project_slug = project_name.lower().replace(" ", "-")
            
            project_gallery_dir = gallery_dir / project_slug
            project_gallery_dir.mkdir(parents=True, exist_ok=True)
            
            jpgs = list(d.glob("*.jpg")) + list(d.glob("*.jpeg")) + list(d.glob("*.JPG")) + list(d.glob("*.JPEG"))
            jpgs.sort()
            
            if not jpgs:
                continue
            
            print(f"Processing {project_name}...")
            
            webp_files = []
            cover_file = f"{project_slug}.webp"
            cover_path = covers_dir / cover_file
            
            for i, img_path in enumerate(jpgs):
                try:
                    with Image.open(img_path) as img:
                        # Fix orientation
                        img = ImageOps.exif_transpose(img)
                        
                        # Generate Cover from first image
                        if i == 0:
                            # Center crop to 16:9, width 1600
                            target_w = 1600
                            target_h = int(1600 * 9 / 16)
                            cover = ImageOps.fit(img, (target_w, target_h), Image.Resampling.LANCZOS)
                            cover.save(cover_path, "WEBP", quality=90)
                        
                        # Generate Gallery Image
                        output_filename = f"{img_path.stem}.webp"
                        output_path = project_gallery_dir / output_filename
                        
                        gallery_img = resize_image(img, 2800)
                        gallery_img.save(output_path, "WEBP", quality=90)
                        
                        aspect = gallery_img.width / gallery_img.height
                        webp_files.append({"filename": output_filename, "aspect": aspect})
                except Exception as e:
                    print(f"Error processing {img_path}: {e}")
            
            if webp_files:
                projects.append({
                    "name": project_name,
                    "slug": project_slug,
                    "cover": f"assets/covers/{cover_file}",
                    "images": webp_files
                })

    # HTML Templates
    header_html = """
    <header>
      <div class="header-left">
        <button class="hamburger">
          <span></span>
          <span></span>
        </button>
        <div class="nav-links">
          <a href="{prefix}index.html" class="nav-link {index_active}">PORTFOLIO</a>
        </div>
      </div>
      <div class="logo"><a href="{prefix}index.html">Nathan So</a></div>
      <div class="header-right">
        <!-- Empty for balance on desktop -->
      </div>
    </header>
    
    <div class="mobile-menu">
      <a href="{prefix}index.html" class="nav-link">PORTFOLIO</a>
    </div>
    """

    footer_html = """
    <footer>
      <div class="footer-left">
        <div class="footer-label">CONTACT VIA</div>
        <div class="footer-links" style="position: relative;">
          <button class="email-copy-btn" id="email-btn">n_so@ucsb.edu</button>
          <div class="copy-popup" id="copy-popup">Copied to clipboard</div>
        </div>
      </div>
      <div class="footer-right">
        <div class="logo-mark">© 2026</div>
      </div>
    </footer>
    """

    base_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="High-end editorial photography portfolio.">
  <link rel="stylesheet" href="{prefix}styles.css">
</head>
<body>
  {header}
  <main>
    {content}
  </main>
  {footer}
  <script src="{prefix}scripts.js"></script>
</body>
</html>
"""

    # Sort projects based on requested order
    order = ['Cars', 'Astrophotography', 'Nature', 'Buildings', 'Motorcycle', 'Concert', 'Animal']
    order_map = {name: i for i, name in enumerate(order)}
    projects.sort(key=lambda p: order_map.get(p["name"], 999))

    # Generate index.html
    grid_items = ""
    for p in projects:
        grid_items += f"""
        <a href="projects/{p['slug']}.html" class="grid-item">
          <div class="grid-image-wrap">
            <img src="{p['cover']}" alt="{p['name']} cover" class="grid-image" loading="lazy" decoding="async">
          </div>
          <div class="grid-meta">
            <span class="grid-title">{p['name']}</span>
          </div>
        </a>
        """
        
    if len(projects) % 2 != 0:
        grid_items += """
        <div class="grid-item more-to-come">
          <div class="grid-image-wrap flex-center">
            <span class="more-text">More to come...</span>
          </div>
        </div>
        """

    index_content = f"""
    <div class="portfolio-grid">
      {grid_items}
    </div>
    """

    index_html = base_html.format(
        title="Portfolio",
        prefix="",
        header=header_html.format(prefix="", index_active="active", contact_active=""),
        content=index_content,
        footer=footer_html
    )

    with open(root_dir / "index.html", "w") as f:
        f.write(index_html)

    # Generate projects/*.html
    lightbox_html = """
    <div class="lightbox" id="lightbox">
      <button class="lightbox-close">
        <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
      <div class="lightbox-controls">
        <button class="lightbox-prev">
          <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <button class="lightbox-next">
          <svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>
      <div class="lightbox-content">
        <img src="" alt="" class="lightbox-img" id="lightbox-img">
      </div>
    </div>
    """

    for p in projects:
        columns = [[], [], []]
        col_heights = [0.0, 0.0, 0.0]
        
        # Sort images by height descending (smallest aspect ratio first) for optimal packing
        sorted_images = sorted(p['images'], key=lambda img: img['aspect'])
        
        for img in sorted_images:
            min_col_idx = col_heights.index(min(col_heights))
            columns[min_col_idx].append(img)
            col_heights[min_col_idx] += 1.0 / img['aspect']
            
        masonry_columns_html = ""
        for col in columns:
            col_items = ""
            for img in col:
                col_items += f"""
                <div class="masonry-item">
                  <img src="../assets/gallery/{p['slug']}/{img['filename']}" alt="Gallery image" loading="lazy" decoding="async">
                </div>
                """
            masonry_columns_html += f'<div class="masonry-column">{col_items}</div>'
            
        project_content = f"""
        <div class="project-hero">
          <h1 class="project-title">{p['name']}</h1>
        </div>
        <div class="masonry">
          {masonry_columns_html}
        </div>
        {lightbox_html}
        """
        
        project_html = base_html.format(
            title=f"{p['name']} - Portfolio",
            prefix="../",
            header=header_html.format(prefix="../", index_active="", contact_active=""),
            content=project_content,
            footer=footer_html
        )
        
        with open(projects_dir / f"{p['slug']}.html", "w") as f:
            f.write(project_html)

    print("Site generated successfully.")

if __name__ == "__main__":
    main()
