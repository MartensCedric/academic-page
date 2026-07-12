---
title: "The Antipodal Method: Fast, Accurate, and Robust 3D Generalized Winding Numbers"
layout: paper

permalink: /publications/antipodal_wn
nav: false

description: We introduce the antipodal method, a fast and accurate algorithm for computing generalized winding numbers for meshes and parametric surfaces, achieving up to 22× speedup over precise CPU methods and 10⁹ queries/second on GPU.
teaser: /assets/img/antipodal_wn/teaser.png
authors: Cedric Martens, Philip Trettner, and Mikhail Bessmeltsev
paper_info: ACM Transactions on Graphics (SIGGRAPH 2026)
date: 2026-07-01
canonical_url: https://cedricmartens.com/publications/antipodal_wn

_styles: >
  .bbb {
    border: 1px solid white;
    border-radius: 3px;
    text-align: center;
    margin-bottom: 10px;
  }
---

  <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        
        .paper-title {
            text-align: center;
            margin-bottom: 10px;
            font-size: 32px;
        }
        
        .venue {
            text-align: center;
            font-size: 19px;
            color: #555;
            margin-bottom: 25px;
        }
        
        .author-container {
            display: flex;
            justify-content: center;
            margin-bottom: 5px;
        }
        
        .author {
            font-size: 18px;
            margin: 0 15px;
        }
        
        .affiliation {
            font-size: 16px;
            color: #666;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .author a {
            color: #0066cc;
            text-decoration: none;
        }
        
        .author a:hover {
            text-decoration: underline;
        }
        
        .teaser {
            width: 100%;
            margin: 20px 0;
            text-align: center;
        }
        
        .teaser img {
            max-width: 80%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        h1 {
            font-size: 24px;
            margin-top: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }
        
        .links {
            margin: 20px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .links a {
            display: inline-block;
            padding: 5px 18px;
            border: 1.5px solid #444;
            color: #333;
            text-decoration: none;
            border-radius: 20px;
            font-size: 14px;
            transition: background-color 0.15s, color 0.15s;
        }

        .links a:hover {
            background-color: #333;
            color: white;
        }

        .citation-box {
            position: relative;
            background-color: #f5f5f5;
            border-radius: 6px;
            padding: 16px 20px;
            overflow-x: auto;
            margin: 12px 0 30px;
        }

        .citation-box pre {
            margin: 0;
            font-size: 13px;
            line-height: 1.6;
            color: #333;
            background: none !important;
            border: none;
            padding: 0;
        }

        .copy-btn {
            position: absolute;
            top: 10px;
            right: 12px;
            background: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 2px 10px;
            font-size: 12px;
            cursor: pointer;
            color: #555;
            transition: background-color 0.15s, color 0.15s;
        }

        .copy-btn:hover {
            background-color: #333;
            color: white;
            border-color: #333;
        }
        
        .abstract {
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }
        
        .teaser-caption {
          text-align: center;
          font-size: 14px;
          color: #666;
          margin-top: 8px;
          font-style: italic;
          max-width: 80%;
          margin-left: auto;
          margin-right: auto;
      }
    </style>

<header class="post-header">
  <h1 class="paper-title">{{ page.title }}</h1>
  <div class="venue">SIGGRAPH 2026</div>
  
  <div class="author-container">
    <div class="author">
        <a href="https://martenscedric.github.io/academic-page/">Cedric Martens</a><sup>*,1</sup>
    </div>
    <div class="author">
        <a href="https://www.graphics.rwth-aachen.de/person/248/">Philip Trettner</a><sup>*,2</sup>
    </div>
    <div class="author">
        <a href="http://www-labs.iro.umontreal.ca/~bmpix/">Mikhail Bessmeltsev</a><sup>1</sup>
    </div>
  </div>
  <div class="affiliation">
      <sup>1</sup> Université de Montréal &nbsp;&nbsp;&nbsp; <sup>2</sup> Shaped Code GmbH<br>
      <small>* Equal Contribution</small>
  </div>
</header>

<div class="teaser">
    <img src="/assets/img/antipodal_wn/teaser.png">
</div>

<div class="abstract">
    <h1>Abstract</h1>
    <p>
        Generalized winding numbers provide a robust measure of point insidedness for 3D surfaces—whether open, self-intersecting, or non-manifold—and are central to numerous geometry processing tasks. However, existing methods trade off between accuracy and computational efficiency, limiting their use in interactive and large-scale applications.
    </p>
    <p>
        We introduce a new formulation and algorithm for computing generalized winding numbers that is both fast and accurate to arbitrary precision, applicable to meshes and parametric surfaces. Our approach expresses the winding number as the sum of two intuitive geometric quantities: the signed number of ray–surface intersections and a boundary integral over the surface's projection onto the unit sphere. This insight leads to an efficient discretization that avoids expensive surface integrals and spherical arrangements.
    </p>
    <p>
        For meshes, our method achieves average speedups of 22× on a CPU compared to the fastest precise methods and 3× compared to the fastest approximation method, while maintaining full precision. On a GPU, for moderately complex meshes we reach a throughput of 10⁹ queries per second, or 4K generalized winding number slices at 120 FPS (13× faster than a naïve GPU method). For parametric surfaces, our method is on average 5.6× faster than the state-of-the-art method, with the same precision. Our method naturally handles complex topologies and non-manifold inputs.
    </p>
</div>

<div class="links">
    <a href="https://dl.acm.org/doi/10.1145/3811323">📄 Paper</a>
    <a href="https://arxiv.org/abs/2605.01536">📝 arXiv</a>
    <a href="https://github.com/MartensCedric/antipodal">💻 Code</a>
</div>

##### Citation

<div class="citation-box">
<button class="copy-btn" onclick="navigator.clipboard.writeText(this.nextElementSibling.textContent).then(() => { this.textContent = '✓ Copied'; setTimeout(() => this.textContent = 'Copy', 2000); })">Copy</button>
<pre>@article{Martens2026AntipodalWN,
  author = {Martens, Cedric and Trettner, Philip and Bessmeltsev, Mikhail},
  title = {The Antipodal Method: Fast, Accurate, and Robust 3D Generalized Winding Numbers},
  year = {2026},
  issue_date = {July 2026},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  volume = {45},
  number = {4},
  issn = {0730-0301},
  url = {https://doi.org/10.1145/3811323},
  doi = {10.1145/3811323},
  journal = {ACM Trans. Graph.},
  month = jul,
  articleno = {43},
  numpages = {11},
  keywords = {winding number, point containment query, robust geometry processing}
}</pre>
</div>

<article>
</article>
