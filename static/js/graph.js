var chart;

function array2highchart(arraydata){
    seriesData=[];
    allData=[];
    seriesNames=[];
    ncol=arraydata[0].length;
    nrow=arraydata.length;
    for(var c=1, len=ncol; c < len; c++){
       //get var names
       seriesNames.push(arraydata[0][c]);
       allData.push(new Array());
    }
//    console.log("alldata");
//    console.log(allData);

    for(var r=1, lenr=nrow; r < lenr; r++){
        dte=new Date(arraydata[r][0]);
        dte=dte.valueOf();
        for(var c=1, lenc=ncol; c < lenc; c++){
            allData[c-1].push([dte, parseFloat(arraydata[r][c])])
        }
    }

    for(var c=1, len=ncol; c < len; c++){
        //seriesData.push({id: c, name: seriesNames[c], data: allData[c], color: seriesColor[c], showInLegend:true});
        seriesData.push({id: c, name: seriesNames[c-1], data: allData[c-1], showInLegend:true});
    }
    console.log("seriesdata");
//    console.log(seriesData);
    return seriesData;
}






function plotTimeSeries(divname, seriesData, title, ylabel){
    $('#'+divname).html("");
    axisdateFormat='%b %Y';
    tipdateFormat='%b %e %Y';
    legendEnable=true;
    tooltipEnable=true;
    scrollbarEnable=false;
    rangeSelEnable=false;
    markerRadius=2;
    lineWidth=1;
    seriesColor="red";
    variableName="test";
    locationName="test";
    measuringUnit="test";

    //creates empty chart. all chart formatting defined here
    chart = Highcharts.chart({
//    chart = new Highcharts.stockChart({
        chart: {renderTo: divname, zoomType: 'xy', marginRight: 0},
        legend: {
            enabled: legendEnable,
            align: 'left',
            x:100,
            y:50,
            verticalAlign: 'top',
            layout: 'vertical',
            floating: true
        },
        credits: {text: '(C) Okavango Research Institute, University of Botswana', enabled: true, href: 'http://www.ori.ub.bw'},
        tooltip: { valueDecimals: 2,
          enabled: tooltipEnable,
	      formatter: function() {
              return "<b>"+this.series.name+'</b> value for <b>' + Highcharts.dateFormat(tipdateFormat, this.x) +
                '</b> is <b>' + this.y + '</b>';
              },
          shared: false		
        },
        scrollbar: {enabled: scrollbarEnable}, 
        navigator: {enabled: false},
        rangeSelector: {enabled: rangeSelEnable},
        xAxis: {type: 'datetime', ordinal: false, dateTimeLabelFormats: {month: axisdateFormat}, showLastLabel: true},
        yAxis: {title: {text: ylabel}, offset: 30, labels:{align: 'right', x: 0, y: 0}, visible: true},
        title: {text: (title).bold()},
        plotOptions: {
            series: {
                marker: {enabled: true, symbol:"circle", radius: markerRadius}, 
                lineWidth: lineWidth}, 
            line: {
                dataGrouping: {enabled:false}}, 
            column: {
                dataGrouping: {enabled:false}, 
                pointWidth: 1}
        },
        series: seriesData,

        exporting: {
            chartOptions: { // specific options for the exported image
                rangeSelector:{enabled:false},
                chart:{marginRight:30},
                plotOptions: {
                    series: {
                        dataLabels: {enabled: false},
                        marker: {enabled: false, symbol:"circle", radius: 1}
                    }
                }
            },
            sourceHeight:400,
            sourceWidth:1000,
            scale:1,
        }
    });
    return true;
}


