# Introduction

This repository is a starting point for new members who want to work with
LiteX. It collects runnable examples, notes on the boards and toolchain
we use, and short explanations of the hardware concepts these
projects rely on.

It does **not** replace the official sources. For the framework itself, see
the [LiteX wiki](https://github.com/enjoy-digital/litex/) and [DeepWiki](https://deepwiki.com/enjoy-digital/litex) (LLM-generated — useful as a map,
but verify against the source).

What you will find here is what those sources cannot cover, as more code
examples, some hardware concepts and so on.

## Motivation

LiteX is powerful but sparsely documented, and most available examples assume
prior familiarity with SoC design. New members end up spending their first
weeks rediscovering the same setup steps and hitting the same errors. This
repository exists to shorten that path, everything here was written while
solving real problems in our projects.

## Repository structure

├── Migen/                # An explanation of the HDL (High-level Description Language) that LiteX uses for all of it's designs \
├── Hardware-Concepts/    # (NOT FINISHED) An intro to low-level concepts about general hardware flow of data \
└── SoC-Architecture/     # (NOT FINISHED) Digital hardware design and System-on-Chip (SoC) construction
