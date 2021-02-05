//-- Touchscreen Behaviour Training Case
//-- Ariel Burman 
//-- Moorman Lab, University of Massachusetts Amherst
//-- v1.1 - November 2020

globalShow = true;

module screwM3(Length,show=false){
  cylinder(h=Length,d=3.4,$fn=40);
  translate([0,0,-3])cylinder(h=3,d=5.5,$fn=40);
  if (show==true) {
    %cylinder(h=Length,d=3,$fn=40);
    %translate([0,0,-3])cylinder(h=3,d=5.5,$fn=40);
    echo("M3 screw [mm]" ,L=Length);
  }
}

module nutM3(show=false) {
  cylinder(h=2.6,d=6.5,$fn=6,center=true);
  if (show==true) {
    %difference(){
      cylinder(h=2.5,d=6.5,$fn=6,center=true);
      cylinder(h=3,d=3.6,$fn=40,center=true);
    }
  }
}


touchL = 121;
touchH = 76;
touchD = 7.8;
//https://osoyoo.com/driver/dsi_screen/5inch-dsi-datasheet.pdf
module touchScreen() {
  translate([0,0,touchH/2])cube([touchL,touchD,touchH],center=true);
  //bending cables
  translate([-touchL/2+11+15,0,-1])cube([30,touchD,2],center=true);
  //raspberryPI
  translate([0,-15-touchD/2,touchH/2]){
    cube([90,30,60],center=true);
    //power connector: 21.5 position of raspi screw, 7.5 from screw, 12.5 from display
    color("red")translate([31,15-12.5,31])cube([9,3,4],center=true);
  }
}


touchSecL = touchL + 11;
touchSecH = touchH + 12;
touchSecD = 4;
module coverRing(show=false){
  difference(){
    translate([0,0,touchSecH/2])cube([touchSecL,touchSecD,touchSecH],center=true);
    translate([0,0,touchSecH/2])cube([touchL-6,touchSecD+.2,touchH-6],center=true);
    for(j=[-1,0,1])
      for(i=[-1,1])
        translate([j*(touchL+3)/2,-touchSecD/2+1.2,touchSecH/2+i*(touchH+4)/2])rotate([90,j*15,0]){
          translate([0,0,-touchSecD-touchD+.5])screwM3(touchD+touchSecD+1);
          nutM3(show);
        }
    translate([touchL/2,0,touchSecH/2])cube([15,touchSecD+.2,25],center=true);
  }
}


boxWallTick = 4.5; //actual tickness is .5 less
boxL = touchSecL+2*boxWallTick;
boxH = touchSecH+2*boxWallTick;
boxD = 80;
module box(show=false){
  difference(){
    translate([0,0,boxH/2])cube([boxL,boxD,boxH],center=true);
    translate([0,-2,boxH/2])cube([touchL+1.6,boxD,touchH+1.6],center=true);
    translate([-touchL/2+11+15,(boxD-touchD)/2-2,boxH/2-touchH/2-1.5])cube([30+2,touchD+1,2+1],center=true);
    
    translate([0,-2-touchD,boxH/2])cube([touchSecL+1,boxD,touchSecH+1],center=true);
    
    //touchscreen
    //outer frame is asimetric
    // open should be 114 x 70
    translate([0,boxD/2-1,boxH/2+1.5])cube([116,4,70],center=true);
    
    //screws
    for(j=[-1,0,1])
      for(i=[-1,1])
        translate([j*(touchL+3)/2,boxD/2+.5,boxH/2+i*(touchH+4)/2])rotate([90,0,0])screwM3(touchD+touchSecD+3,show);
    
    //M3 screws for cover
    for(i=[0,1])mirror([i,0,0])
      translate([boxL/2+.1,-boxD/2+6,boxH/2+5])rotate([0,-90,0])screwM3(boxWallTick+8,show);
    
    //cables
    translate([31,boxD/2-2-touchD-12.5,boxH-boxWallTick/2])cylinder(h=boxWallTick+1,d=innerDbase+5.8,$fn=60,center=true);
    
    //holes for plate
    translate([boxL/2-boxWallTick,-boxD/2-.5,boxWallTick-.5])cube([boxWallTick+1,55,9]);
    translate([boxL/2+.5,-12,14]){
      for(i=[-1,1])translate([0,i*22.75,18])rotate([0,-90,0])screwM3(boxWallTick+1);
      translate([0,0,18])rotate([0,-90,0])cylinder(h=boxWallTick+1,d=8,$fn=30); //d=15
    }
  }
}


module cover(show=false){
  translate([0,-boxWallTick/2,boxH/2])cube([boxL,boxWallTick,boxH],center=true);
  translate([0,.5,boxH/2])cube([touchSecL,2,touchSecH],center=true);
  for(i=[0,1])mirror([i,0,0])
    translate([touchSecL/2-2.5,6,boxH/2+5])
    difference() {
      union(){
        cube([5,10,10],center=true);
        translate([0,-2,0])cube([5,6,20],center=true);
      }
      for(i=[-1,1])translate([0,1,i*10.5])rotate([0,90,0])cylinder(h=6,d=11,center=true,$fn=100);
      translate([-1.3,0,0])
      rotate([30,0,0])rotate([0,90,0])nutM3(show); //M3 nut
      translate([3,0,0])rotate([0,-90,0])screwM3(6); //M3 screw
    }
}


cableCL = 130; //min 35
cableCLbase = 30;
innerD = 9;
innerDbase= 18;
module cableCoverHalf(show=false) {
  difference(){
    union(){
       cylinder(h=cableCLbase+3,d=innerDbase+5,$fn=50);
       translate([0,0,boxWallTick])cylinder(h=3,d1=innerDbase+5+3,d2=innerDbase+5,$fn=50);
       hull(){
        translate([0,0,cableCLbase+2])cylinder(h=1,d=innerDbase+5,$fn=50);
        translate([0,0,cableCLbase+7])cylinder(h=1,d=innerD+5,$fn=50);
       }
       cylinder(h=cableCL,d=innerD+5,$fn=50);
    }
    translate([0,0,-1])cylinder(h=cableCLbase+2,d=innerDbase,$fn=50);
    hull(){
        translate([0,0,cableCLbase])cylinder(h=1,d=innerDbase,$fn=50);
        translate([0,0,cableCLbase+5])cylinder(h=1,d=innerD,$fn=50);
    }
    translate([0,0,cableCLbase+5])cylinder(h=cableCL,d=innerD,$fn=50);
    translate([-innerDbase/2-4.5,-innerDbase-9,-1])cube([innerDbase+9,innerDbase+9,cableCL+2]);
  }
  
  //wings for screws
  translate([innerD/2+2+5,1,cableCL-5])
  difference(){
    union(){
      translate([-2.5,0,0])cube([5,2,10],center=true);
      rotate([90,0,0])cylinder(h=2,d=10,$fn=80,center=true);
    }
    translate([0,1.5,0])rotate([90,0,0])screwM3(7,show);
  }

  mirror([1,0,0])  
  translate([innerD/2+2+5,1,cableCL-5])
  difference(){
    translate([0,1,0])
    union(){
      translate([-3,0,0])cube([6,4,10],center=true);
      rotate([90,0,0])cylinder(h=4,d=10,$fn=80,center=true);
    }
    translate([0,2,0])rotate([90,0,0])nutM3(show);
    translate([0,-3,0])rotate([-90,0,0])screwM3(4);
  }
}


module plate(){
  difference(){
    translate([-53/2,0,0])cube([53,1,33]);
    translate([0,-.5,18])rotate([-90,0,0])cylinder(h=2,d=15,$fn=30);
    for(i=[-1,1])translate([i*22.75,-.5,18])rotate([-90,0,0])cylinder(h=2,d=4.5,$fn=30);
  }
  difference(){
    union(){
      hull(){
        translate([-53/2,0,-1])cube([53,1,1]);
        translate([0,35/2+1,-.5])cylinder(h=1,d=35,$fn=30,center=true);
      }
      translate([0,35/2+1,-4])cylinder(h=8,d1=25,d2=33,$fn=30,center=true);
      translate([0,-20,-8])cube([5,30,5]);
    }
    translate([0,35/2+1,-3]) cylinder(h=7,d1=22,d2=27,$fn=30,center=true);
  }
}


module sensorC(show=false){
  difference(){
    union(){
      translate([0,0,0])cube([53,5,25],center=true);
      for(i=[0,1])mirror([i,0,0])translate([-20,13,-5])cube([8+2,20+4,11+4],center=true);
    }

    translate([0,-2,0])cube([40,5,21],center=true);
    for(i=[0,1])mirror([i,0,0])translate([-20,13+2-5,-5])translate([.75,-2,0])cube([8.6,20+10,11],center=true);
    for(i=[-1,1])translate([i*22.75,3.2,5.5])rotate([90,0,0])screwM3(14,show);
    *translate([0,-12,5])rotate([-90,0,0])cylinder(h=27,d=15,$fn=30); //d=15
    translate([0,0,-7.5])cube([26,6,12],center=true);
  }
  difference(){
    translate([0,0,-6.5])cube([30,5,12],center=true);
    translate([0,0,-7.5])cube([26,6,12],center=true);
  }
}


/////////////////////////
////show
/////////////////////////
translate([31,boxD/2-2-touchD-12.5,boxH-boxWallTick]){
  cableCoverHalf(globalShow);
  rotate([0,0,180])cableCoverHalf(globalShow);
}

box(globalShow);
translate([0,-boxD/2-10.0,0])cover(globalShow);

////color("white")
translate([0,boxD/2-touchD/2-2,(-touchH+boxH)/2]){
  touchScreen();
  translate([0,-touchSecD/2-touchD/2,-(touchSecH-touchH)/2]) coverRing(globalShow);
}

translate([(touchL+11)/2-6.5,-12,13])
rotate([0,0,-90]) plate();

translate([boxL/2+2.5,-12,14+13])
rotate([0,0,-90]) sensorC(globalShow);


/////////////////////////
////print
/////////////////////////
//translate([0,-boxH/2,boxD/2])rotate([-90,0,0])box();
//translate([0,boxH/2,5])rotate([90,0,0])cover();
//translate([0,cableCL/2,0])rotate([90,0,0])cableCoverHalf();
//rotate([90,0,0])sensorC();