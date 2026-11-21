# IT incident - 14 July 2025

A retry bug in the checkout service wrote some West region orders twice on 14 July. Finance should exclude duplicated order rows (same date, product, quantity and region) from reports.
