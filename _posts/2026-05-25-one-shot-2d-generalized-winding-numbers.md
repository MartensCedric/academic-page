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

Determining whether a point lies *inside* or *outside* of a shape is a classical problem in computer graphics. Consider the polygon below and the query points A and B. Evidently, point A should be considered "inside", whereas point B "outside". How do we compute this algorithmically?

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig1_simple_polygon.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="We consider Point A to be inside the shape and point B to be outside. The polygon's outline is the boundary between the inside region and outside region." %}
</div>

There is actually a straightforward solution: shoot a ray originating at the query point and count the number of intersections. If you get an **even** number, the query point is outside, if it's **odd**, you're inside. This essentially works because the shape is the boundary between the two regions: (1) inside and (2) outside. When you shoot a ray and follow it, every intersection you encounter means that you change regions, either from inside to outside or vice-versa. This technique is called *raycasting*.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig2_raycasting.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="To determine whether a point is inside or outside, we can compute its crossing number. This is done by casting a ray and counting the number of intersections with the shape (crossings) and the counting its parity." %}
</div>

## Open Geometry

Geometry in computer graphics is not guaranteed to be closed and watertight. In practice, we encounter *open* shapes that cannot form an explicit boundary between what is considered inside and outside. Returning to our raycasting example, any gap in the polygon could remove an intended intersection and then result in a wrong answer.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig3_gap.svg" class="img-fluid rounded z-depth-1" max-width="300px" caption="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor." %}
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
