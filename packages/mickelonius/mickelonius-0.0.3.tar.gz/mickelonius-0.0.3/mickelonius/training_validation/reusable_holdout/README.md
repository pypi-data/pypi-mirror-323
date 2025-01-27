# Differential Privacy For Adaptive Queries

## Introduction
This document contains notes and expositions of the proofs used to justify and prove
the efficacy of using differential privacy to reuse a holdout or validation dataset
in an optimization paradigm where the metrics computed on the validation or holdout
dataset are used to modify or optimize an algorithm on a separate training set. **This
allows one to train on the training set and validate on the holdout dataset continually, 
up to a defined, but parameterized, limit or "budget."**

Note that this is a very deep subject and I make no claims of completeness or rigor. 
This is a conceptual document that takes the mathematical exposition as far as necessary 
to facilitate a deeper understanding.

### Definitions and Problem Setup
We have a function, $\phi: \chi \to [0,1]$, on the distribution $P$, referred to as a linear functional of $P$. A request for an approximation to the expectation of a bounded function on $\chi$, $P[\phi] = \mathbb{E}_{x \sim P} \phi(x)$, of some function of $P$, is called a statistical query.

A dataset, $S = (x_1, \ldots, x_n)$, consists of $n$ samples drawn randomly and independently from the distribution $P$ over a discrete universe $\chi$ of possible data points. A natural estimator of $P[\phi]$ is $\mathcal{E}_S \equiv \frac{1}{n} \sum_{i=1}^{n} \phi(x_i)$. The Hoeffding inequality says that for a fixed function $\phi$, the probability (over the choice of dataset) that the estimator $\mathcal{E}_S$ has an error greater than $\tau$ is no more than $2e^{-2\tau^2n}$.

## Max-Information and Differential Privacy

### Max-Information
#### Definition
Let $\mathbf{X}$ and $\mathbf{Y}$ be jointly distributed random variables. The **max-information** between $\mathbf{X}$ and $\mathbf{Y}$, denoted $I_{\infty}(\mathbf{X}; \mathbf{Y})$, is the minimal value of $k$ such that for every $x$ in the support of $\mathbf{X}$ and every $y$ in support of $\mathbf{Y}$, we have:

$$
P[\mathbf{X} = x | \mathbf{Y} = y] \leq 2^k P[\mathbf{X} = x]
$$

This definition is a lower bound on the amount of dependence that $\mathbf{X}$ has on $\mathbf{Y}$. The random variable $\mathbf{S}$ is drawn i.i.d. from $P^n$ and random variable $\phi$ is as above, where an analyst may arrive at $\phi$ with foreknowledge of other $\phi$ from $\mathbf{\phi}$. Let’s say for each function $\phi$ in support of $\mathbf{\phi}$, we have a set of bad datasets, $R(\phi)$, which cause the empirical value $\mathcal{E}_S[\phi]$ to be far from the true value $P[\phi]$, i.e., $\phi$ overfits to $S$. The max-information we defined above will allow us to bound the probability of overfitting, $P[S \in R(\phi)]$:

#### Theorem
For $k = I_{\infty}(\mathbf{S}, \mathbf{\phi})$, $P[\mathbf{S} \in R(\phi)] \leq 2^k \max_{\phi} P[\mathbf{S} \in R(\phi)]$.

**Proof:**

Since $k = I_{\infty}(\mathbf{S}, \mathbf{\phi})$, we need $P[\mathbf{S} = S | \mathbf{\phi} = \phi] \leq 2^k P[\mathbf{S} = s]$ to be true for all $S$ and $\phi$. Then,

$$
P[\mathbf{S} \in R(\phi)] = \sum_{\phi} P[\mathbf{S} \in R(\phi) | \mathbf{\phi} = \phi] P[\mathbf{\phi} = \phi]
$$
$$
\leq 2^k \max_{\phi} P[\mathbf{S} \in R(\phi)]
$$

Thus, if we limit the mutual information between $\mathbf{S}$ and $\mathbf{\phi}$, we can bound the probability of the non-desirable outcome $\mathbf{S} \in R(\phi)$.

### Differential Privacy
Let’s say we have two datasets, $x$ and $y$, that differ by only one record or data point. We then refer to $x$ and $y$ as **adjacent**.

#### Definition
A randomized algorithm $\mathcal{M}$ with domain $\mathcal{X}^n$ is $(\epsilon, \delta)$-differentially private if for all $\mathbf{S} \in \text{Range}(\mathcal{M})$ and for all pairs of adjacent datasets $x, y \in \mathcal{X}^n$:

$$
P[\mathcal{M}(x) \in S] \leq \exp(\epsilon) P[\mathcal{M}(y) \in S] + \delta
$$

where the probability is over the random variable $\mathcal{M}$. The case where $\delta = 0$ is known as **pure differential privacy** and is sometimes referred to as $\epsilon$-differentially private.

**Intuition:** If $|\epsilon|$ is small, then the probability of getting $S$ for $\mathcal{M}(x)$ is nearly the same as for $\mathcal{M}(y)$. In other words, it’s difficult, from a statistical perspective, to learn much about the record in which $x$ and $y$ differ.

### Using Differential Privacy to Bound Max-Information
#### Lemma
Let $\mathcal{M}$ be an $\epsilon$-differentially private algorithm. Let $\mathbf{S}$ be any random variable over $n$-element input datasets for $\mathcal{M}$, and let $\mathbf{Y}$ be the corresponding output distribution $\mathbf{Y} = \mathcal{M}(\mathbf{S})$. Then, $I_{\infty}(\mathbf{S}; \mathbf{Y}) \leq (\log_2 e) \epsilon n$.

**Proof:**

By Bayes' rule, $I_{\infty}(\mathbf{S}; \mathbf{Y}) = I_{\infty}(\mathbf{Y}; \mathbf{S})$. Since any two datasets $S$ and $S'$ differ by at most $n$ records,

$$
P[\mathbf{Y} = y | \mathbf{S} = S] \leq e^{\epsilon n} P[\mathbf{Y} = y | \mathbf{S} = S']
$$

Thus, $I_{\infty}(\mathbf{S}; \mathbf{Y}) \leq (\log_2 e) \epsilon n$.

### Thresholdout Algorithm
The **Thresholdout** algorithm provides a way to interact with a holdout dataset using differential privacy. Here’s an outline of the algorithm:

#### Algorithm
> For a given function $\phi: \mathcal{X} \mapsto [0,1]$:
> 1. Initialize $\hat{T} \gets T + \gamma$ for $\gamma \sim Lap(2\sigma)$.
> 2. While $B > 0$:
>     a. Sample $\xi \sim Lap(\sigma)$, $\gamma \sim Lap(2\sigma)$, and $\eta \sim Lap(4\sigma)$.
>     b. If $|\mathcal{E}_{S_h}[\phi] - \mathcal{E}_{S_t}[\phi]| > \hat{T} + \eta$, then:
>         - Output $\mathcal{E}_{S_h}[\phi] + \xi$.
>         - Decrement $B$, update $\hat{T} \gets T + \gamma$.
>     c. Else:
>         - Output $\mathcal{E}_{S_t}[\phi]$

**Lemma**  
Thresholdout satisfies $\left( \frac{2B}{\sigma n}, 0 \right)$-differential privacy.  
Thresholdout also satisfies $\left( \frac{\sqrt{32B \log(2/\delta)}}{\sigma n}, \delta \right)$-differential privacy for any $\delta > 0 \).

## Experiment

#### No feature correlation, Standard Holdout
![NoCorr_StandardHoldout.jpg](NoCorr_StandardHoldout.jpg)

#### No feature correlation, Thresholdout
![NoCorr_Thresholdout.jpg](NoCorr_Thresholdout.jpg)

Making the first twenty variables correlated:

#### First 20 features correlated, Standard Holdout
![20Corr_StandardHoldout.jpg](20Corr_StandardHoldout.jpg)
#### First 20 features correlated, Thresholdout
 ![20Corr_Thresholdout.jpg](20Corr_Thresholdout.jpg)