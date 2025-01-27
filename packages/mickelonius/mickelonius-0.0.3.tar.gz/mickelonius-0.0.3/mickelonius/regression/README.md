# Regression Modeling


## Introduction
This is a more formal exposition of the various types of regression modeling covered in [23Reg]. The main technical reference is [Hastie], but [Fox, Bishop] are referenced also.

There are three types of variables we deal with:  
- **Categorical** or **discrete** variables belong to a finite set $g \in \mathcal{G}$,  
- **Numerical** variables, which are real numbers,  
- **Ordered categorical** (e.g., $g \in \{\textit{Small}, \textit{Medium}, \textit{Large}\}$).

Input variables are generically referred to as $X$. If $X$ is a vector, the $j^{th}$ component is referred to as $X_j$. Output variables are referred to as $Y$ or $G$, if the output is a **categorical** variable. The $i^{th}$ data point of $X$ is denoted as $x_i$. Matrices are denoted by bold uppercase letters. For a set of $N$ input vectors with $p$ components, $\mathbf{X}$ is an $N \times p$ matrix. One row of $\mathbf{X}$ is not bold: $x_i$. The $j^{th}$ column of $\mathbf{X}$ is bold: $\mathbf{x}_j$. Estimates or predictions of $Y$ are denoted as $\hat{Y}$.

### Numerical Output
The idea is to find a function $f(X)$ to compute $\hat{Y}$. For all numerical variables ($X \in \mathbb{R}^{p}, Y \in \mathbb{R}$) and a joint distribution $Pr(X,Y)$, we define the **Expected Prediction Error (EPE)** as the integral of a **loss function** $\mathcal{L}(Y, f(X))$. If we define $\mathcal{L}(Y, f(X)) = [Y - f(X)]^2$, it is known as **squared error loss**:

$$
EPE(f) = \int \mathcal{L}(Y, f(X)) = E[(Y - f(X))^2]
$$
$$
EPE(f) = \int [y - f(x)]^2 Pr(dx, dy)
$$

If we condition on $X$, we can write EPE as:

$$
EPE(f) = E_X E_{Y|X}([Y - f(X)]^2 | X)
$$

For each instance of $X$, or $x$, we can minimize EPE pointwise:

$$
f(x) = argmin_{c}{( E_{Y|X}([Y - c]^2 | x)}
$$

The solution becomes:

$$
f(x) = E_{Y|X}(Y | X = x)
$$

### Discrete Output
For a **categorical** variable where $g \in \mathcal{G}$, the loss function $\mathbf{L}$ is a $K \times K$ matrix where $K = \text{card}(\mathcal{G})$ and $L(k, l)$ is the loss value for predicting the class $\mathcal{G}_l$ when the truth is $\mathcal{G}_k$. The EPE becomes:

$$
EPE = E[L(G, \hat{G}(X))]
$$

where $G$ is the truth and $\hat{G}(X)$ is the estimate or result of the classifier. For a joint distribution $Pr(\mathcal{G}, X)$:
$$
EPE = E_X \sum_{k=1}^{K} L[\mathcal{G}_k, \hat{G}(X)] Pr(\mathcal{G}_k | X)
$$

Similar to the numerical output scenario, we can minimize EPE pointwise:
$$
\hat{G}(x) = argmin_{g \in \mathcal{G}} \sum_{k=1}^{K} L[\mathcal{G}_k, g] Pr(\mathcal{G}_k | X = x)
$$

which simplifies to:

$$
\hat{G}(x) = argmin_{g \in \mathcal{G}} [1 - Pr(g | X = x)]
$$

or:

$$
\hat{G}(x) = \mathcal{G}_k \textrm{ if } Pr(\mathcal{G}_k | X = x) = \max_{g \in \mathcal{G}} Pr(g | X = x)
$$

This solution is known as the **Bayes classifier**, which classifies based on the most probable class using $Pr(G | X)$. This gives a Bayes-optimal decision boundary. The error rate using that decision boundary is known as the **Bayes rate**, which is used to compare the performance of other classifiers.

## Numerical Outcomes

### Linear Regression
In linear regression, we aim to predict a real-valued value $Y$, using an input vector $X = (X_1, X_2, \ldots, X_p)$. The model is:

$$
f(X) = \beta_0 + \sum_{j=1}^{p} X_j \beta_j
$$

An assumption here is that the regression function $E(Y | X)$ is actually linear in $X$. Let the vector of linear coefficients be $\beta = (\beta_1, \beta_2, \ldots, \beta_p)^T$ and $\mathbf{X}$ be the $N \times (p+1)$ input matrix. We use the square of the sum of residuals $(y - \hat{y})$, also denoted as $RSS$ for a particular value of $\beta$:

$$
RSS(\beta) = \sum_{i=1}^{N}(y_i - f(x_i))^2 = \sum_{i=1}^{N}(y_i - \beta_0 - \sum_{j=1}^{p} x_{ij} \beta_j)^2
$$

In a more concise matrix/vector form:

$$
RSS(\beta) = (\mathbf{y} - \mathbf{X} \beta)^T (\mathbf{y} - \mathbf{X} \beta)
$$

Taking the first partial derivative of $RSS$ with respect to $\beta$, setting the result to zero, and solving for $\hat{\beta}$, we get:

$$
\frac{\partial RSS}{\partial \beta} = -2 \mathbf{X}^T (\mathbf{y} - \mathbf{X} \beta) = 0
$$
$$
\hat{\beta} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}
$$

The predicted output values $\hat{y}$ can now be predicted:

$$
\hat{y} = \mathbf{X} \hat{\beta} = \mathbf{X} (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}
$$

Something to note: colinearity between input variables in $X$ manifests itself in a singular or ill-conditioned $\mathbf{X}^T \mathbf{X}$ matrix.

### Inference
In order to draw inferences about the parameters and the model, we make a few more assumptions. The conditional expectation of $Y$ is linear in $X_1, \ldots, X_p$:

$$
Y = E(Y | X_1, \ldots, X_p) + \epsilon
$$
$$
Y = \beta_0 + \sum_{j=1}^{p} X_j \beta_j + \epsilon
$$

where the error $\epsilon$ is a Gaussian random variable with mean 0 and variance $\sigma^2$, or $\epsilon \sim N(0, \sigma^2)$.

### Shrinkage Methods

#### Ridge Regression
Ridge regression reduces regression coefficients by penalizing the $RSS$ by the total size of all coefficients. The model looks like the following:

$$
\hat{\beta}^{ridge} = argmin_{c}{\beta} \left\{ \sum_{i=1}^{N} (y_i - \beta_0 - \sum_{j=1}^{p} x_{ij} \beta_j)^2 + \lambda \sum_{j=1}^{p} \beta_j^2 \right\}
$$

In matrix form:

$$
RSS(\lambda) = (\mathbf{y} - \mathbf{X} \beta)^T (\mathbf{y} - \mathbf{X} \beta) + \lambda \beta^T \beta
$$

Then:

$$
\hat{\beta}^{ridge} = (\mathbf{X}^T \mathbf{X} + \lambda \mathbf{I})^{-1} \mathbf{X}^T \mathbf{y}
$$

## Categorical and Ordinal Outcomes

### Logistic Regression

