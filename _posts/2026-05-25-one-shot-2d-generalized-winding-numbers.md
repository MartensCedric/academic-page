---
layout: post
title: The One-Shot Method in 2D
short_name: One-Shot in 2D
date: 2026-05-25 12:00:00-0400
description: >
tags: geometry math
categories:
related_posts: false
---

Notes for Cedric :
It should be clear how raycasting and winding numbers are related
The naive raycasting should be well motivated (not useless information)
It should be clear that winding numbers are oriented
Transition from shape to curve should be clear.

## Inside-Outside Tests

Determining whether a point lies *inside* or *outside* of a shape is a classical problem in computer graphics. Consider the polygon below and two query points A and B. Intuitively, point A is inside the polygon and point B is outside. 

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig1_simple_polygon.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="Points A and B are separated by the polygon's outline which separates the inside and outside regions." %}
</div>

How do we compute this algorithmically? Given a query point and the line segments of a polygon, how do we determine whether this point is inside or outside of that shape?

A solution: shoot a ray originating at the query point, in any direction, and count the number of intersections. If there is an **odd** number of intersections, the query point lies inside the shape. Accordingly, the query point is outside if there is an **even** number of intersections. This algorithm works because [the polygon separates the plane into two distinct regions](https://en.wikipedia.org/wiki/Jordan_curve_theorem): inside and outside. As the ray crosses the polygon, each intersection alternates the current region, making parity (even/odd). This *raycasting* technique is known as the [even-odd rule](https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule).

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig2_raycasting.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="To determine whether a point is inside or outside of a shape, we can perform a parity test via raycasting. In other words, we shoot a ray originating at the query point in any direction, count the number of intersections, and test whether that number is odd or even." %}
</div>

## Bad Geometry

Geometry in computer graphics is not guaranteed to be closed and watertight (really?). In practice, we encounter *open* shapes that do not form separate inside and outside regions. Returning to our raycasting example, any gap in the polygon (no matter how small) creates potential for failure cases the even-odd rule algorithm. These gaps remove intended intersections and can then result in a wrong answer.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig3_gap.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="The even-odd rule algorithm requires closed shapes. If the shape is open, there are gaps where intersections are missed." %}
</div>

## Winding Numbers

To solve this problem, we will need to discuss generalized winding numbers. Unlike the previous section, where we discussed an unoriented polygon, winding numbers require the polygons to have an *orientation*.

The *winding number* is the number of times a curve winds around a point. This is a **signed** quantity — the orientation of the curve matters. Let's look at a few examples:

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig4_winding_numbers.svg" class="img-fluid rounded z-depth-1" max-width="520px" caption="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor." %}
</div>

The winding number enables us to answer our original problem, how do we compute whether a point is inside or outside? For regular polygons, a winding number of **zero** means that our point is outside, and **1** means that it is inside. With winding numbers, we could also get a negative value or a number greater than one. Depending on your application you might or might not consider these points to be inside. However, winding numbers alone do not help.

To compute the winding number, there are different methods, but we can do it via raycasting. Instead of looking at whether the total number of intersections is even or odd, we will instead look at the **signed sum** of these intersections.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig5_signed_intersections.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor." %}
</div>

## Generalized Winding Numbers

*Generalized winding numbers* are a relaxation of winding numbers to open curves. Instead of a discrete numbers of windings, we will use a fractional value. It's equivalent to the limit of taking a bunch of rays and computing the average value of the signed sum of intersections.
