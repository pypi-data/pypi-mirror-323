# PatANN

## Overview
PatANN is a massively parallel, distributed, and scalable in-memory/on-disk vector database library for efficient nearest neighbor search across large-scale datasets by finding vector patterns.

PatANN leverages patterns for data partitioning like Google ScANN, implements disk-based I/O similar to DiskANN, and employs search techniques akin to HNSWlib, resulting in an algorithm that synthesizes the best features to outperform existing approaches.

## Status
**Beta Version**: Currently uploaded for benchmarking purposes. Complete documentation and updates are under development. Not for production use yet.

## Platforms
**Beta Version**: Restricted to Linux to prevent premature circulation of beta version
**Production Releases (late Feb 2024)***: Will support all platforms that are supported by mesibo

## Key Features
- Faster Index building and Searching
- Supports both in-memory and on-disk operations
- Dynamic sharding and load balancing across servers
- Advanced search, filtering and pagination
- Unlimited scalability without pre-specified capacity

## Algorithmic Approach
- Combines NSW (Navigable Small World) graph with a novel pattern based partitioning algorithm
- Preliminary results show phenomenal performance in building index and searching
- Potential slight variations in lower-end matching

## Contributions Welcome
We are seeking help to:
- Run additional datasets
- Validate and improve the algorithm

## Contact
For queries, please contact: support@mesibo.com

## Disclaimer
Results may vary. Detailed research paper forthcoming.
