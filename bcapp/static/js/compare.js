// 쿼리 결과 값 저장 변수
dataset = [];
dataset1 = [];
var day = ['월', '화', '수', '목', '금', '토', '일']

for(var i=0; i < day.length; i++) {
    if(i >= stepcount_1.length) {
        dataset.push({'name': day[i], 'value': null});
    } else {
        dataset.push({'name': day[i], 'value': parseInt(stepcount_1[i])});
    }  
}

for(var i=0; i < day.length; i++) {
    if(i >= stepcount_2.length) {
        dataset1.push({'name': day[i], 'value': null});
    } else {
        dataset1.push({'name': day[i], 'value': parseInt(stepcount_2[i])});
    } 
}


// y축 ticks 설정
data_max = [];
data_max.push({'value' : d3.max(dataset, d => d.value)});
data_max.push({'value' : d3.max(dataset1, d => d.value)});

data_min = [];
data_min.push({'value' : d3.min(dataset, d => d.value)});
data_min.push({'value' : d3.min(dataset1, d => d.value)});


// 기본적인 마진값
var width = 300;
var height = 300;
var margin = {top: 40, left: 40, bottom: 70, right: 5};

// canvas 사이즈
var svg = d3
  .select("#vis")
  .append("svg")
  .attr("width", width)
  .attr("height", height)

// graph 사이즈
var graph = svg
  .append("g")
  .attr("width", width)
  .attr("height", height)
  .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// 축 범위 설정
var x = d3
  .scaleBand()
  .domain(dataset1.map(d => d.name))
  .range([ 0, width - margin.left ])
  .padding(0.5);

var y = d3
  .scaleLinear()
  .domain([d3.min(data_min, d => (d.value/100)*90), d3.max(data_max, d => (d.value/100)*105)]).nice()
  .range([ height - margin.bottom, 0]);

// axis groups
var xAxisGroup = graph
  .append("g")
  .attr("class", "x-axis")
  .style("font-size", "11px")
  .attr("transform", "translate(0," + (height - margin.bottom) + ")");
  

var yAxisGroup = graph
  .append("g")
  .style("font-size", "9px")
  .attr("class", "y-axis");

// create axes
var xAxis = d3
  .axisBottom(x)

  
var yAxis = d3
  .axisLeft(y)
  .ticks(6)

// call axes
xAxisGroup.call(xAxis).selectAll('line').remove();
yAxisGroup.call(yAxis).selectAll('line').remove();

// gridlines in y axis function
function make_y_gridlines() {		
  return d3.axisLeft(y)
      .ticks(6)
}

// add the Y gridlines
graph.append("g")			
.attr("class", "grid")
.attr('fill','none')
.attr('stroke', '#DCDCDC')
.attr('stroke-width',0.1)
.attr('shape-rendering','crispEdges')
.call(make_y_gridlines()
    .tickSize(-width)
    .tickFormat("")
)


// d3 Line path generator *****
var line = d3
  .line()
  .x(function(d) {
    
      return x(d.name) + 10;
  })
  .y(function(d) {
    return y(d.value);
  });

// line path element
var path = graph.append("path");

// update line path data *****
path
.attr("d", line(dataset)) 
.attr("fill", "none")
.attr("stroke", "#fd7e14")
.attr("stroke-width", 2);

var line1 = d3
  .line()
  .x(function(d) { 
  
    return x(d.name) + 10;

  })
  .y(function(d) {
    return y(d.value);
  });

// line path element
var path1 = graph.append("path");

// update line path data *****
path1
.attr("d", line1(dataset1)) 
.attr("fill", "none")
.attr("stroke", "#198754")
.attr("stroke-width", 2);