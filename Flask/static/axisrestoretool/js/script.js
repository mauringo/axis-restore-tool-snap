var switchMonitorVal= false;

function switchMonitor(){
    switchMonitorVal=! switchMonitorVal;
   
}


function httpGet(theUrl) {   let reqHeader = new Headers();
    reqHeader.append('Content-Type', 'text/json');
    let initObject = {
        method: 'GET', headers: reqHeader,
    };

    return fetch(theUrl,initObject)
        .then((response) => { 
            return response.json().then((data) => {
                //console.log(data);
                return data;
            }).catch((err) => {
                console.log(err);
            }) 
        });

}


function populate() {
var mypromise=(httpGet(location.origin+"/axisrestoretool/staticdata"));
mypromise.then((data) => {
    //console.log(data);
    var singleaxes=0;
    var doubleaxes=0;
    document.getElementById('axesnumber').innerHTML="Axes Number: "+data.length;
    for (d in data) {
       if(data[d].subDeviceCount==2){
        doubleaxes++;
       }
       else{
        singleaxes++;
       }
    }
    document.getElementById('singleaxes').innerHTML="Single Axes: "+singleaxes;
    document.getElementById('doubleaxes').innerHTML="Double Axes: "+doubleaxes;
    usageinfo();
  });

}


function backupAny() {
    var mypromise=(httpGet(location.origin+"/axisrestoretool/backupany"));
    mypromise.then((data) => {
        //console.log(data);
        var singleaxes=0;
        var doubleaxes=0;
        document.getElementById('axesnumber').innerHTML="Axes Number: "+data.length;
        for (d in data) {
           if(data[d].subDeviceCount==2){
            doubleaxes++;
           }
           else{
            singleaxes++;
           }
        }
      });
    
    }
function restoreAny() {
        var mypromise=(httpGet(location.origin+"/axisrestoretool/restoreany"));
        mypromise.then((data) => {
            //console.log(data);
            var singleaxes=0;
            var doubleaxes=0;
            document.getElementById('axesnumber').innerHTML="Axes Number: "+data.length;
            for (d in data) {
               if(data[d].subDeviceCount==2){
                doubleaxes++;
               }
               else{
                singleaxes++;
               }
            }
          });
        
        }




    

function usageinfo() {
    var mypromise=httpGet(location.origin+"/axisrestoretool/backuprestoreinfo");

    mypromise.then((data) => {
        console.log(data);
        var backupvalue = 0;
        var restorevalue=0;
        var countbackup = 0;
        var counterstore=0;
        var backupdone=0;
        var restoredone=0;
        var backupData=[];
        var restoreData=[];
        for (d in data) {

            var myinfos = data[d].info
           
            for(i in myinfos){
                backupDataElement={};
                restoreDataElement={};
                backupDataElement.drive=data[d].drive;
                backupDataElement.ip=data[d].ip;
                restoreDataElement.drive=data[d].drive;
                restoreDataElement.ip=data[d].ip;

                if (myinfos[i].export!=null){
                    backupDataElement.status=myinfos[i].export.state;
                    if(myinfos[i].export.state=="failed"){
                        backupDataElement.status=myinfos[i].export.state+" "+myinfos[i].export.progressInfo;
                    }
                    
                    backupDataElement.progress=myinfos[i].export.progress;
                    if(myinfos[i].export.progress<100){
                        backupvalue+=myinfos[i].export.progress;
                        countbackup++;
                    }
                    else{
                        backupdone++;
                    }
                }
                else{
                     
                    backupDataElement.status="nodata"
                    backupDataElement.progress="nodata"
                }
                if (myinfos[i].import!=null){
                     
                    restoreDataElement.status=myinfos[i].import.state;
                    restoreDataElement.progress=myinfos[i].import.progress;
                    if(myinfos[i].import.progress<100){
                        restorevalue+=myinfos[i].import.progress;
                        counterstore++;
                    }
                    else{
                        restoredone++;
                    }
                }
                else{
                     
                    restoreDataElement.status="nodata"
                    restoreDataElement.progress="nodata"
                }
                backupData.push(backupDataElement);
                restoreData.push(restoreDataElement);
            }
           
         }   
        updateTable(backupData,"backuptable");
        updateTable(restoreData,"restoretable");

        if(countbackup!=0){
            backupvalue = backupvalue/countbackup;
        }
        else if(backupdone!=0){
            backupvalue = 100;
        }
        if(counterstore!=0){
            restorevalue = restorevalue/counterstore;
        }
        else if(restoredone!=0){
            restorevalue = 100;
        }
        
        
        
        $('#backup').attr('aria-valuenow', backupvalue).css('width', `${backupvalue}%`);
        $('#restore').attr('aria-valuenow', restorevalue).css('width', `${restorevalue}%`);
    

       
        document.getElementById('backuplabel').innerHTML= 'Backup Status: '+ backupvalue+'%';
        document.getElementById('restorelabel').innerHTML= 'Restore Status: '+restorevalue +'%';
   
            

        if (switchMonitorVal){
            //processesInfo();
        }
        else{
            //clearTable("cputable");
            //clearTable("ramtable");
        }
        });
      
    }

    function processesInfo() {
        var mypromise=httpGet(location.origin+"/cpumonitoring/processes");

        mypromise.then((data) => {
            
            
            updateTable(data.cpuProcesses,"cputable");
            updateTable(data.ramProcesses,"ramtable");
            });
            
        }

    function updateTable(data,tablename) {
        
        var rows = []
        var tablecontents;
        for (var i = 0; i < data.length; i++) {
          rows.push({
           
            Drive: data[i].drive,
            IP: data[i].ip,
            Satus:data[i].status,
            Progress:data[i].progress,

          })
          
        }
       
        
        var tablecontents = '    <th data-field="Drive">Drive</th>  <th data-field="IP">IP</th> <th data-field="Satus">Satus</th>  <th data-field="Progress">Progress</th>';

        tablecontents += "<tbody>";
        for (var i = 0; i < rows.length; i++) {
            
            tablecontents += "<tr>";
                tablecontents += "<td>" + rows[i].Drive + "</td>";
                tablecontents += "<td>" + rows[i].IP + "</td>";
                tablecontents += "<td>" + rows[i].Satus + "</td>";
                tablecontents += "<td>" + rows[i].Progress + "</td>";
            tablecontents += "</tr>";
            
        }
        tablecontents += "</tbody>";
        document.getElementById(tablename).innerHTML = tablecontents;

       
    
      }

      function updateTableTemp(data,tablename) {
        
        var rows = []
        var tablecontents;
       
        for (var i = 0; i < data.length; i++) {
          rows.push({
           
            PID: data[i][0],
            Name: data[i][1],
            username:data[i][2],
            RAM:data[i][3]
            
          })
          
        }
       
        console.log(rows);
        var tablecontents = ' <thead>  <tr>    <th data-field="PID">Device</th>  <th data-field="username">Temperature </th><th data-field="RAM">High value</th> <th data-field="CPU">Critical Value</th>     </tr>  </thead>';

        tablecontents += "<tbody>";
        for (var i = 0; i < rows.length; i++) {
            
            tablecontents += "<tr>";
           
                tablecontents += "<td>" + rows[i].PID + "</td>";
                tablecontents += "<td>" + rows[i].Name + "</td>";
                tablecontents += "<td>" + rows[i].username + "</td>";
                tablecontents += "<td>" + rows[i].RAM + "</td>";
              
            tablecontents += "</tr>";
            
        }
        tablecontents += "</tbody>";
        document.getElementById(tablename).innerHTML = tablecontents;

       
    
      }
    
      function clearTable(tablename) {
        
        
     

        var tablecontents = ' <thead>  <tr>    <th data-field="PID">PID</th>   <th data-field="Name">Name</th><th data-field="username">username</th><th data-field="RAM">RAM</th> <th data-field="CPU">CPU</th>     </tr>  </thead>';
       
        document.getElementById(tablename).innerHTML = tablecontents;

       
    
      }


setInterval(function() {

    usageinfo();
    //loadMyGraph();

}, 2000);

function loadMyGraph(){
    
    loadGraph(graph1,color1,title1,range1,CpuX, CpuY);
    loadGraph(graph2,color2,title2,range2,CpuX, RamY);
}




var graph1='CPUgraph';
var color1='#0079fc';
var data1='CPU';
var range1=[0, 100];
var title1='CPU %';

var graph2='RAMgraph';
var color2='#27a849';
var data2='RAM';
var range2=[0, 100];
var title2='RAM %';
            
var CpuX=[];
var CpuY=[];
var RamX=[];
var RamY=[];    
