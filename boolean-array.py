a = np.zeros((138*87), dtype=bool)
a[np.random.choice(138*87, 1000, replace=False)] = 1
a = a.reshape(138, 87)

a[8, :].sum()
a[:, 8].sum()
