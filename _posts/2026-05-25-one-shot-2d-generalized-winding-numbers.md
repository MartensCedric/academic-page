---
layout: post
title: One-Shot 2D Generalized Winding Numbers
date: 2026-05-25 12:00:00-0400
description: >
tags: geometry math
categories:
related_posts: false
---

Notes:
It should be clear how raycasting and winding numbers are related
The naive raycasting should be well motivated (not useless information)
It should be clear that winding numbers are oriented
Transition from shape to curve should be clear.

This post's goal is to provide a concise and accessible introduction to the One-Shot method. I will begin with inside-outside tests and raycasting, which provides some intuition of the method. Then, I will introduce Generalized Winding Numbers, with the One-Shot algorithm.

Determining whether a point lies inside or outside of a shape is a classical problem in computer graphics. Consider the polygon below and the query points A and B. Evidently, point A should be considered "inside", whereas point B "outside". How do we compute this algorithmically?

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig1_simple_polygon.svg" class="img-fluid rounded z-depth-1" max-width="300px" %}
</div>

There is actually a straightforward solution: shoot a ray originating at the query point and count the numbre of intersections. If you get an even number, the query point is outside, if it's odd, you're inside. This essentially works because the shape is the boundary between the two regions: (1) inside and (2) outside. When you shoot a ray and follow it, every intersection you encounter means that you change regions, either from inside to outside or vice-versa.

<div class="text-center">
{% include figure.liquid path="assets/img/blog/one-shot-winding-numbers/fig2_raycasting.svg" class="img-fluid rounded z-depth-1" max-width="300px" %}
</div>

In practice, not all the geometry in computer graphics is closed and watertight. We encounter open geometry or some that are intended to be closed but contain gaps. Any gap or opening removes an intended intersection and can disastrously result in the wrong result. 

[Figure: Showing the wrong result due to a gap in the shape.]

To solve this problem, we will need to discuss generalized winding numbers. Unlike the previous section, where we discussed an unoriented polygon, winding numbers require the polygons to have an orientation.

The winding number is the number of times a curve winds around a point. This is a signed quantity, the orientation of the curve matters. Let's look at a few examples:

[Figure: Shows integer winding number of different curves and different points]

The winding number enables us to answer our original problem, how do we compute whether a point is inside or outside? For regular polygons, a winding number of zero means that our point is outside, and 1 means that it is inside. With winding numbers, we could also get a negative value or a number greater than one. Depending on your application you might or might not consider these points to be inside. However, winding numbers alone do not help.

To compute the winding number, there are different methods, but we can do it via raycasting. Instead of looking at whether the total number of intersections is even or odd, we will instead look at the signed sum of these intersections. 

[Figure: Sum of signed intersections]

Generalized winding numbers are a relaxation of winding numbers to open curves. Instead of a discrete numbers of windings, we will use a fractioanl value. It's equivalent to the limit of taking a bunch of rays and computing the average value of the signed sum of intersections.

