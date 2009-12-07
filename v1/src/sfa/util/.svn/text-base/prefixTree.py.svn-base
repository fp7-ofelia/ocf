class prefixNode:

    def __init__(self, prefix):
        self.prefix = prefix
        self.children = []
    

class prefixTree:
    
    def __init__(self):
        self.root = prefixNode("")

    def insert(self, prefix, node = None):
        """
        insert a prefix into the tree
        """
        if not node:
            node = self.root

        parts = prefix.split(".")
        length = len(parts)

        if length > 1:
            for i in range(1, length + 1):
                name = ".".join(parts[:i])
                if not self.exists(name) and not name == prefix:
                    self.insert(name)
         
        if prefix.startswith(node.prefix):
            if prefix == node.prefix:
                pass
            elif not node.children:
                node.children.append(prefixNode(prefix))
            else:
                inserted  = False
                for child in node.children:
                    if prefix.startswith(child.prefix):
                        self.insert(prefix, child)
                        inserted = True
                if not inserted:
                    node.children.append(prefixNode(prefix)) 

    def load(self, prefix_list):
        """
        load a list of prefixes into the tree
        """
        for prefix in prefix_list:
            self.insert(prefix)

    def exists(self, prefix, node = None):
        """
        returns true if the specified prefix exists anywhere in the tree,
        false if it doesnt. 
        """
        if not node:
            node = self.root

        if not prefix.startswith(node.prefix):
            return False
        elif node.prefix == prefix:
            return True
        elif not node.children:
            return False
        else:
            for child in node.children:
                if prefix.startswith(child.prefix):
                    return self.exists(prefix, child)

    def best_match(self, prefix, node = None):
        """
        searches the tree and returns the prefix that best matches the 
        specified prefix  
        """
        if not node:
            node = self.root
        
        if prefix.startswith(node.prefix):
            if not node.children:
                return node.prefix
            for child in node.children:
                if prefix.startswith(child.prefix):
                    return self.best_match(prefix, child)
            return node.prefix
         
    def dump(self, node = None):
        """
        print the tree
        """
        if not node:
            node = self.root
            print node.prefix

        for child in node.children:
            print child.prefix, 
         
        for child in node.children:
            self.dump(child)
