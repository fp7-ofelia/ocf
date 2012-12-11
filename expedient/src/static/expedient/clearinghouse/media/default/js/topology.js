
/*
	LOOP DETECTION
*/

function translate_path(flowvisorPath, portList, nodeMap){
//
//Translates the IDs of the ports into the IDs of the nodes, obtaining a node graph ready to check the loops in the topology.
//
//flowvisorPAth: The port map selected by the user. Example:{"a1":["b1"],"a2":["c1"],"b1":["a1"],"c1":["a2"]}
//portList: Array of ports used. Example: ["a1","a2","b1","c1"]
//nodeMap: Dictionary where the key are the ports and the value are the belonging switch. Example:{"a1":"A","a2":"A","b1":"B","c1":"C"}
//This function using the examples above will return: {"A":["B","C"],"B":["A"],"C":["A"]}
//
        FVPTranslated = new Object();
        for (var attr in flowvisorPath){
                if(FVPTranslated[nodeMap[attr]]){
                         
                        FVPTranslated[nodeMap[attr]].push(nodeMap[flowvisorPath[attr]])
                        if (count_elements(FVPTranslated[nodeMap[attr]],nodeMap[flowvisorPath[attr]])>1){
                                return false; // there are two switchs interconected by two diferent ports {"A":["B","B"],"B":["A","A"]}
                        };
                } else {
                        
                        FVPTranslated[nodeMap[attr]] = [nodeMap[flowvisorPath[attr]]]
                };
        };
        return check_for_loops(FVPTranslated);
};
function check_for_loops(topology){
//
// Check if there are any loop in the topology selected, returning true if there are no loops and false if there are loops.
//

       	var usedSwitchs  = get_used_switchs(topology)
        var path = new Array();
        var visited = usedSwitchs.pop();// pointer to the current node visited
        var lastVisited = visited; // pointer of the last node visited
        var noLoop = true; 
        var allowedReps = 1; // if path has more than one elements equal, there is a loop. 
        var maxTTL = 100 // max number of iterations of while loop in order to no take much time
        var TTL = 0; // number of iterations of the while loop.
        var mem = undefined;

        /////////////////////////////////////////////////////////////////////////////////////////////////////   
        /* //Uncomment this to run the test mode. Used switchs must contain all switchs of topo except visited
        //TESTS// 
        //var topo = '{"A":["B","C"],"B":["A","C"],"C":["B","A"]}';// Triangular loop
        //var topo = '{"A":["B"],"B":["A","C"],"C":["B"]}';// Liniar topology
        //var topo = '{"A":["B","C"],"B":["A"],"C":["A"]}';// Star Topology     
        var topo ='{"A":["B","C","D"],"B":["A"],"C":["A","E"],"D":["A","F"],"E":["C","F"],"F":["D","E"],  "G":["H"],"H":["G","I"],"I":["H"]}';//mixed topology
        var topology = JSON.parse(topo);
        var usedSwitchs = ['A','B','C','D','E','F','H','I'];
        visited = 'G';
        lastVisited = 'G';
        //END OF TESTS
        *////////////////////////////////////////////////////////////////////////////////////////////////////

        if (topology[visited] == undefined){ //empty topology avoiding
                return true;
        };
        path.push(visited);
        while ((noLoop)&&(TTL<100)){
                if (count_elements(path,visited) > allowedReps){ // Two equal elements in path means a loop
                        noLoop = false;
                        break;
                };
                if((mem == undefined)&&(usedSwitchs.length == 0)&&((topology[visited].length == 0)||(String(topology[visited])==String(lastVisited)))){
                        //Job finished, no loops found
                        break;
                }else{
                        topology[visited]=delete_from_array(topology[visited],lastVisited); // Nodes are strongly connected, taking account this, no false 
                                                                                            // loops will be detected 

                        // Thes algortihm is based on DFS searchs.
                        // Visiting a node different situations can occur:
                        // First Situation: The visited node is connected to more than one nodes. 
                        if (topology[visited].length > 1){
                                //Choose to visit a node and save the location of the other switchs to visit later.
                                lastVisited = visited;
                                if (mem == undefined){
                                        mem = new Object();
                                };
                                mem[visited]= topology[visited];
                                visited = mem[visited].pop();
                                usedSwitchs = delete_from_array(usedSwitchs,visited);
                        // Second Situation: The visited node is connected only to one node.
                        }else if(topology[visited].length == 1){
                                // Vistit this node 
                                lastVisited = visited;
                                visited = topology[visited];
                                usedSwitchs = delete_from_array(usedSwitchs,visited);
                        // Third Situation: The visited switch is an end-point without loops, but there are still switchs to visit stored in mem.
                        }else if((topology[visited].length == 0)&&!(mem == undefined)){
                                // check mem and look for switchs to visit and go to the top again. If all the switchs in mem are visited, undefine mem  
                                for (var node in mem){
                                        if (mem[node] == "done"){
                                                continue;
                                        }else{
                                                mem[node]=delete_from_array(mem[node],lastVisited);
                                                if (!(mem[node].length == 0)){
                                                        visited = mem[node].pop()
                                                };
                                                if (mem[node].length == 0){     
                                                        mem[node] = "done";
                                                lastVisited = node;
                                                usedSwitchs = delete_from_array(usedSwitchs,visited);
                                                break;
                                                };
                                        };
                                
                                };
                                mem = undefined
                        // Fourth situation: There are no loops in the followed path, but in topology there are unvisited nodes 
                        // (they are not connected to the followed path, but are selected by the user)
                        }else if(!(usedSwitchs.length == 0)){
                                // Take as visited this node and go to the top.
                                visited = usedSwitchs.pop();
                                lastVisited = visited;
                        };
                };
                TTL++;
                path.push(visited)
        };
        return noLoop;
};

/* Useful Functions */

function delete_from_array(list,item){
        if (list == undefined){
                return [];
        };
        index = list.indexOf(String(item));
        if (index > -1){
                list.splice(index,1);
        };
        return list;
        
};
function count_elements(list,item){
        var counter = 0;
        for(var i=0;i<list.length;i++) {
                if (String(list[i]) === String(item)) counter++;
        };
        return counter;
};
function get_used_switchs(FVSwitchPath){
        UsedSwitchs = new Array()
        for (var FVswitch in FVSwitchPath) {
                UsedSwitchs.push(FVswitch);
        };
        return UsedSwitchs
};
/* 
	END OF LOOP DETECTION
*/
