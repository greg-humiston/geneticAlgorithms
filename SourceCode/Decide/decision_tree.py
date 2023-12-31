import argparse
import collections
import math
import operator
import pickle
import random

def potential_leaf_node(data):
  count = collections.Counter([i[-1] for i in data])
  return count.most_common(1)[0] #the top item

def entropy(data):
  frequency = collections.Counter([item[-1] for item in data])
  def item_entropy(category):
    ratio = float(category) / len(data)
    return -1 * ratio * math.log(ratio, 2)
  return sum(item_entropy(c) for c in frequency.values())

def best_feature_for_split(data):
  baseline = entropy(data)
  def feature_entropy(f):
    def e(v):
      partitioned_data = [d for d in data if d[f] == v]
      proportion = (float(len(partitioned_data)) / float(len(data)))
      return proportion * entropy(partitioned_data)
    return sum(e(v) for v in set([d[f] for d in data]))
  features = len(data[0]) - 1
  information_gain = [baseline - feature_entropy(f) for f in range(features)]
  best_feature, best_gain = max(enumerate(information_gain),
		                key=operator.itemgetter(1))
  return best_feature

def create_tree(data, label):
  category, count = potential_leaf_node(data)
  if count == len(data):
    return category
  node = {}
  feature = best_feature_for_split(data)
  feature_label = label[feature]
  node[feature_label]={}
  classes = set([d[feature] for d in data])
  for c in classes:
    partitioned_data = [d for d in data if d[feature]==c]
    node[feature_label][c] = create_tree(partitioned_data, label)
  return node

def classify(tree, label, data):
  root = list(tree.keys())[0]
  node = tree[root]
  index = label.index(root)
  for k in node.keys():
    if data[index] == k:
      if isinstance(node[k], dict):
        return classify(node[k], label, data)
      else:
        return node[k]

def as_rule_str(tree, label, ident=0):
  space_ident = '  '*ident
  s = space_ident
  root = list(tree.keys())[0]
  node = tree[root]
  index = label.index(root)
  for k in node.keys():
    s +=  'if ' + label[index] + ' = ' + str(k)
    if isinstance(node[k], dict):
      s += ':\n' + space_ident  + as_rule_str(node[k], label, ident + 1)
    else:
      s += ' then '  + str(node[k]) + ('.\n' if ident == 0 else ', ')
  if s[-2:] == ', ':
    s = s[:-2]
  s += '\n'
  return s

def data_points(height, width):
  #(0,0) is in the middle
  data = []
  for i in range(100):
    x = random.randint(-width, width)
    y = random.randint(-height, height)
    data.append([x, y, not (-width/2. < x < width/2.) and not (-height/2. < y < height/2.)])
  return data

def five_points():
  data = [[0, 0, False],
        [-1, 0, True],
        [1, 0, True],
        [0, -1, True],
        [0, 1, True]]

  label = ['x', 'y', 'out']
  tree = create_tree(data, label)
  print(tree)
  print(as_rule_str(tree, label))
  category = classify(tree, label, [1, 1])
  print(category)

def demo():
  data = [['a', 0, "good"], ['b', -1, "bad"], ['a', 101, "good"]]
  label = ['letter', 'number', 'class']
  tree = create_tree(data, label)
  print (tree)
  print (as_rule_str(tree, label))
  category = classify(tree, label, ['b', 101])
  print (category)

  data = [[0, 0, False], [1, 0, False], [0, 1, True], [1, 1, True]]
  label = ['x', 'y', 'out']
  tree = create_tree(data, label)
  print(tree)
  print(as_rule_str(tree, label))
  category = classify(tree, label, [1, 1])
  print(category)
  category = classify(tree, label, [1, 2])
  print(category)

  data = data_points(6, 6)
  label = ['x', 'y']
  tree = create_tree(data, label)
  print (tree)
  print (as_rule_str(tree, label))
  print ("[-1, 1]", classify(tree, label, [-1, 1]))
  print ("[-4, 4]", classify(tree, label, [-4, 4]))
  print ("[-10, 10]", classify(tree, label, [-10, 10]))

def find_edges(tree, label, X, Y):
  X.sort()
  Y.sort()
  diagonals = [i for i in set(X).intersection(set(Y))]
  diagonals.sort()
  L = [classify(tree, label, [d, d]) for d in diagonals]
  low = L.index(False)
  min_x = X[low]
  min_y = Y[low]

  high = L[::-1].index(False)
  max_x = X[len(X)-1 - high]
  max_y = Y[len(Y)-1 - high]

  return (min_x, min_y), (max_x, max_y)

def tennis():
  data = [["sunny", "hot", "high", False, False],
    ["sunny", "hot", "high", True, False],
    ["overcast", "hot", "high", False, True],
    ["rain", "mild", "high", False, True],
    ["rain", "cool", "normal", False, True],
    ["rain", "cool", "normal", True, False],
    ["overcast", "cool", "normal", True, True],
    ["sunny", "mild", "high", False, False],
    ["sunny", "cool", "normal", False, True],
    ["rain", "mild", "normal", False, True],
    ["sunny", "mild", "normal", True, True],
    ["overcast", "mild", "high", True, True],
    ["overcast", "hot", "normal", False, True],
    ["rain", "mild", "high", True, False]]
  label = ["outlook", "temperature", "humidity", "windy", "play"]
  tree = create_tree(data, label)
  print (tree)
  print (as_rule_str(tree, label))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--datafile", help="Pickled data points")
  fns = {"demo": demo, "five_points": five_points, "tennis": tennis}
  parser.add_argument("-f", "--function",
      choices = fns,
      help="One of " + ', '.join(fns.keys()))
  args = parser.parse_args()

  try:
    L = []
    if args.datafile:
      with open(args.datafile, 'rb') as f:
        L = pickle.load(f)
        print (L[0])
        label=['x'+str(i) for i in range(1, len(L[0])+1)]
        label[0]='x'
        label.append("y")
        tree = create_tree(L, label)
        print (tree)
        print (as_rule_str(tree, label))
        print(find_edges(tree, label, [x[0] for x in L], [x[0] for x in L]))
    else:
      args = parser.parse_args()
      f = fns[args.function]
      f()
  except KeyError as ke:
    print (ke)
    parser.print_help()
