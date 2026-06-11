---
layout: post
title: The One-Shot Method in 2D
short_name: One-Shot in 2D
date: 2026-05-25 12:00:00-0400
description: >
tags: geometry math
categories:
related_posts: false
annotations: true
---

## Inside-Outside Tests

Determining whether a point lies *inside* or *outside* of a shape is a classical problem in computer graphics. Consider the polygon below and two query points A and B. Intuitively, point A is inside the polygon and point B is outside. 

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig1_simple_polygon.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="Point A is inside and point B is outside." %}
</div>

How could we determine this inside-outside classification algorithmically, using the query point and the polygon's line segments?

A solution: shoot a ray originating at the query point, in any direction, and count the number of intersections. If there is an **odd** number of intersections, the query point lies inside the shape. Accordingly, if there is an **even** number of intersections, the query point lies outside the shape. This algorithm works because [the polygon separates the plane into two distinct regions](https://en.wikipedia.org/wiki/Jordan_curve_theorem): inside and outside. As the ray crosses the polygon, it moves from one region to the other, alternating between entering and exiting the shape. This *raycasting* technique is known as the [even-odd rule](https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule). The method has a few edge cases to consider, but to keep this post brief, we will not discuss them.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig2_raycasting.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="To determine whether a point lies inside or outside of a shape, we can perform a parity test via raycasting: shoot a ray originating at the query point in any direction, count the number of intersections, and test whether that number is odd or even. An odd parity result indicates that the query point is inside the shape." %}
</div>

## Open Geometry

Geometry in computer graphics is not guaranteed to be closed. In practice, we encounter *open* shapes that do not partition the space in inside and outside regions, this is especially true for 3D meshes{% include annotation.liquid text="Nearly 15% of the models used in the 3D printing community are open, as demonstrated by the Thingi10K dataset (Zhou, 2016)." %}. The even-odd rule algorithm breaks down on open shapes, the gaps remove intended intersections, leading to an incorrect containment result.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig3_gap.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="The even-odd rule algorithm requires closed shapes." %}
</div>

A good question here is: What even is "inside" for an open shape?

**Generalized** Winding Numbers enable us to compute whether a point lies inside or outside of an open shape, but before introducing them, we should discuss (regular) winding numbers, since they are a natural extension.

## Winding Numbers

Unlike the previous section that uses unoriented polygons, winding numbers require orientation. In addition, it is more advantageous here to see the shapes as oriented 2D curves.

The *winding number* of a query point with respect to an **oriented** curve is the number of times that  this curve winds around the point. This is a **signed** quantity, where the orientation of the curve matters. Let's look at a few examples:

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig4_winding_numbers.svg" class="img-fluid rounded z-depth-1" max-width="520px" caption="The winding number at a query point of an oriented curve is the number of times the curve winds around the point. Depending on the orientation of the curve, the winding number can be negative or of higher absolute value than 1. For a closed curve, winding numbers are always integer-valued." %}
</div>

Winding numbers can be used to answer inside-outside queries. A point with a winding number of one is inside, and a point with a winding number of zero is outside. For values besides one and zero, we can use the non-zeror rule: consider all values as inside except zero which is inside.

To compute winding numbers, we can also use a raycasting technique. Instead of looking at whether the total number of intersections is even or odd, we can look at the **signed sum** of these intersections.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig5_signed_intersections.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor." %}
</div>

## Generalized Winding Numbers

*Generalized winding numbers* (GWN) are a relaxation of winding numbers to open curves, resulting in decimal values instead of integers. They can be approximated by computing the average signed intersection value of multiple rays. Note that there are several other existing methods computing 2D GWNs, I cover this raycasting approach because it intuitively builds our One-Shot method.l 

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig6_gwn_field.svg" class="img-fluid rounded z-depth-1" max-width="720px" caption="Averaging the result of the raycasting approach leads to the Generalized Winding Number (GWN) as the number of rays increases." %}
</div>

In our paper (Martens, 2025), we propose a method to compute generalized winding numbers by shooting a single ray. Rather than shooting a multitude of rays, our approach shoots a ray and computes a boundary term, which in 2D is simply the angle between the endpoints, and then obtain the exact GWN of that query point.

Why does the angle between the endpoints suffice? The key observation is that, as we **rotate** a ray around the query point, its signed-intersection count changes **only when the ray sweeps past an endpoint** of the curve. Everywhere else the count is constant, so the whole averaging-over-rays computation collapses to a single boundary term that depends only on the endpoints.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig7a_sweep.svg" class="img-fluid rounded z-depth-1" max-width="820px" caption="A tangled open curve and a query point P. As the ray rotates it stabs the curve several times (blue = +1, red = −1), yet the signed sum S holds at +1 through both loops and every tangency — and only steps to +2 once the ray sweeps past an endpoint." %}
</div>

Summing this up over every ray direction at once, the two rays from P through the curve's endpoints carve the plane into sectors of constant signed count. The signed sum is the same for every ray within a sector, and the boundaries between sectors are exactly the endpoint directions.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig7c_sectors.svg" class="img-fluid rounded z-depth-1" max-width="440px" caption="The two rays through the curve's endpoints split every direction into just two sectors of constant signed count: aim a ray into the upper sector and S = +2, into the lower one and S = +1. The sector boundaries are exactly the endpoint directions." %}
</div>

