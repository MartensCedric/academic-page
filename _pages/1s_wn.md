---
title: One-Shot Method for Computing Generalized Winding Numbers
layout: paper

permalink: /publications/1s_wn
nav: false

description: We propose an alternative method to compute a generalized winding number, based only on the surface boundary and the intersections of a single ray with the surface. 
teaser: /assets/img/1s_wn/overview.pdf
authors: Cedric Martens and Mikhail Bessmeltsev
paper_info: Symposium on Geometry Processing 2025
date: 2025-06-03

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
            margin-bottom: 30px;
            font-size: 32px;
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
            margin: 30px 0;
        }
        
        .links a {
            display: inline-block;
            margin-right: 15px;
            padding: 4px 15px;
            background-color: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        
        .links a:hover {
            background-color: #0055aa;
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
  
  <div class="author-container">
    <div class="author">
        <a href="https://martenscedric.github.io/academic-page/">Cedric Martens</a>
    </div>
    <div class="author">
        <a href="http://www-labs.iro.umontreal.ca/~bmpix/">Mikhail Bessmeltsev</a>
    </div>
    </div>
    <div class="affiliation">
        Université de Montréal
    </div>
</header>

<div class="teaser">
    <img src="/academic-page/assets/img/1s_wn/overview.png">
    <div class="teaser-caption">
        Overview of the basic algorithm: Given a surface with a
boundary (a), we project the boundary onto a unit sphere around
the query point (b, blowup in c). The boundary splits the surface of
the sphere into regions (d). We shoot a single ray through each of
those regions, and compute the number of signed intersections χi
of each ray with the surface.
    </div>
</div>

<div class="abstract">
    <h1>Abstract</h1>
    <p>
       The generalized winding number is an essential part of the geometry processing toolkit, allowing to quantify how much a given
point is inside a surface, even when the surface has boundaries and noise. We propose a new universal method to compute
a generalized winding number, based only on the surface boundary and the intersections of a single ray with the surface,
supporting any oriented surface representations that support a ray intersection query. Due to the focus on the boundary, our
algorithm has a unique set of properties. For 2D parametric curves, on a regular grid of query points, our method is up to 4×
faster than the current state of the art, maintaining the same precision. In 3D, our method can compute a winding number of a
surface without discretizing it, including parametric surfaces. For some meshes with many triangles and a simple boundary, our
method is faster than the hierarchical evaluation of the generalized winding number while still being precise. Similarly, on some
parametric surfaces with a simple boundary, our method can be faster than adaptive quadrature. We validate our algorithms
theoretically, numerically, and by demonstrating a gallery of results on a variety of parametric surfaces and meshes, as well
uses in a variety of applications, including voxelizations and boolean operations.
    </p>
</div>

<div class="links">
    <h1>Links</h1>
    <a href="https://www-labs.iro.umontreal.ca/~bmpix/one_shot/1S_GWN.pdf">Paper (PDF)</a>
    <a href="">Code (Coming Soon)</a>
    <a href="https://arxiv.org/abs/2408.04466">Preprint</a>
</div>

##### Citation
```
@article{Martens2025WindingNumberOneShot,
  title = {One-Shot Method for Computing Generalized Winding Numbers},
  author = {Martens, Cedric and Bessmeltsev, Mikhail},
  journal = {Computer Graphics Forum},
  volume = {44},
  number = {5},
  year = {2025},
}
```


<article>
    <!-- Additional content sections would go here -->
    <!-- For example: Introduction, Methods, Results, etc. -->
</article>


