---
layout: post
title: The One-Shot Method in 2D
short_name: One-Shot in 2D
date: 2026-06-14 12:00:00-0400
description: >
tags: geometry math
categories:
related_posts: false
annotations: true
permalink: /blog/one_shot_2d_gwn/
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

Geometry in computer graphics is not guaranteed to be closed. In practice, we encounter *open* shapes that do not partition the space into inside and outside regions, this is especially true for 3D meshes{% include annotation.liquid text="Nearly 15% of the 3D printing models in the Thingi10K dataset (Zhou, 2016) are open surfaces." %}. The even-odd rule algorithm breaks down on open shapes, the gaps remove intersections, leading to an incorrect containment result.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig3_gap.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="The even-odd rule algorithm requires closed shapes." %}
</div>

A good question here is: What even is "inside" for an open shape?

**Generalized** Winding Numbers enable us to compute whether a point lies inside or outside of an open shape, but before introducing them, we should discuss (regular) winding numbers, since they are a natural extension.

## Winding Numbers

Unlike the previous section that uses unoriented polygons, winding numbers require orientation. In addition, it is more advantageous here to see the shapes as oriented 2D curves.

The *winding number* of a query point with respect to an **oriented** curve is the number of times that this curve winds around the point. This is a **signed** quantity, where the orientation of the curve matters. The location of the point matters. Let's look at a few examples:

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig4_winding_numbers.svg" class="img-fluid rounded z-depth-1" max-width="520px" caption="The winding number at a query point of an oriented curve is the number of times the curve winds around the point. When a point is outside, the winding number is zero (top-left). The sign of the winding number depends on the orientation of the curve (top-right, bottom-left). A curve can wind multiple times around a point (bottom-right). Winding numbers are always integer-valued." %}
</div>

Winding numbers can be used to answer inside-outside queries. A point with a winding number of one is inside, and a point with a winding number of zero is outside. For values other than one and zero, we can use the non-zero rule: consider all values as inside with the exception of zero being outside.

To compute winding numbers, we can also use a raycasting technique. Instead of computing the parity of the intersections, instead we look at the **number of signed intersections**. These intersections are signed: they add +1 when the ray intersects the curve in a counter-clockwise manner, and -1 clockwise. To clarify, for a ray shot towards the right, an intersection with the oriented curve going upwards is counter-clockwise (+1), if the curve goes downwards it is clockwise (-1). 

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig5_signed_intersections.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="Point A is inside because the number of signed intersections is 1. Point B is outside because the number of signed intersections is -1 + 1 = 0. The first intersection is clockwise with respect to the ray (-1) and the second one is counter-clockwise (+1)." %}
</div>

Similar to the earlier parity test, the direction of the ray is arbitrary. Given a query point, the sum of signed intersections does not depend on the chosen ray direction.


## Generalized Winding Numbers

*Generalized winding numbers* (GWN) are a relaxation of winding numbers to open curves. For closed curves, the chosen ray direction does not affect the result, however, this is not true on open curves.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig6_gwn_field.svg" class="img-fluid rounded z-depth-1" max-width="720px" caption="Left: Computing the winding number from a single ray results in an inconsistent result that depends on the ray direction. Instead, averaging the result of multiple rays (Middle, Right) leads to a smoother field." %}
</div>

Rather than considering a point as strictly inside or strictly outside, we can recover a continuous notion of insideness: Generalized Winding Numbers. They expensive to compute via naively raycasting, but possible. Generalized Winding Numbers can be approximated by shooting a multitude of rays, creating a smooth field that is only discontinuous across the curve.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig8_gwn_curves.svg" class="img-fluid rounded z-depth-1" max-width="720px" caption="The GWN field for three curves. Left: An open curve where the GWN value is close to 1 for points that are nearly inside; Middle: A closed curve with positive and negative integer GWN based on the winding direction around each enclosed region; Right: an open spiral that has GWN values exceeding 2." %}
</div>

There are other existing methods computing 2D GWNs; I cover this raycasting approach because it intuitively builds our One-Shot method.
 
In our paper [(Martens, 2025)]({{ '/publications/1s_wn.html' | relative_url }}), we propose a method to evaluate generalized winding numbers that only requires shooting a single ray and computing the angle between the endpoints.

While the naive approach would be to shoot a multitude of rays and average them all, the key observation is that: **the number of signed intersections only changes at the endpoints**. 

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig7a_sweep.svg" class="img-fluid rounded z-depth-1" max-width="820px" caption="As we rotate a ray around the query point, the number of signed intersections is constant (χ = 1) until we cross an endpoint (χ = 2)." %}
</div>

In other words, the endpoints divide the plane into two regions where all rays shot within the same region share the same number of signed intersections (χ). 

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig7c_sectors.svg" class="img-fluid rounded z-depth-1" max-width="440px" caption="Given a query point P and an open oriented curve, the endpoints of the curve define two regions where the number of signed intersections is constant." %}
</div>

Moreover, each region's χ differs by exactly one. Then, only a single ray is needed to compute the χ of both regions. As we rotate a ray counter-clockwise and encounter the start of the oriented curve, χ increases by 1, and it decreases by 1 when we encounter the endpoint. Then, with a single ray we can compute both χ values required to compute the Generalized Winding Number!

## The One-Shot Method

Putting this all together, we conceptually want to compute the average number of signed intersections, naively obtained by shooting nearly an infinite amount of rays. With the One-Shot method, only a single ray is required to compute the sum of signed intersections (χ) constant in each of the two regions. To evaluate the GWN at a query point, we weighted-sum the χ values of each region by the fraction of the circle that the region occupies, computed as the angle between endpoints in radians.

$$
w(p) = \frac{\theta_1}{2\pi}\,\chi_1 + \frac{\theta_2}{2\pi}\,\chi_2
$$

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig9_angle_weights.svg" class="img-fluid rounded z-depth-1" max-width="440px" caption="The endpoints create two regions of angular length of θ₁ and θ₂ (with θ₁ + θ₂ = 2π). Within each region, the sum of signed intersections χ is constant and differs by exactly one across each region. " %}
</div>


## Interactive Generalized Winding Number
{% include gwn_bezier_applet.liquid %}

## What's Next

That concludes the brief introduction to the One-Shot Method in 2D. If you are interested in knowing more about winding numbers, here are a few links:

- [One-Shot Method Website]({{ '/publications/1s_wn.html' | relative_url }})
- [Perspectives on Winding Numbers](https://nzfeng.github.io/research/WNoDS/PerspectivesOnWindingNumbers.pdf)
- [The Antipodal Method Website](https://martenscedric.github.io/academic-page/publications/antipodal_wn.html)

