//-- Touchscreen Behaviour Training Case
//-- Ariel Burman, University of Massachusetts
//-- v1.0 - November 2020

touchL = 132;
touchH = 87;
touchD = 6;

module touchscreen() {
  difference(){
    translate([-touchL/2,-touchD/2,0])cube([touchL,touchD,touchH]);
    for(j=[-1,0,1])
     for(i=[0,1])
      translate([j*(touchL-6)/2,4,2.5+i*(touchH-5)])rotate([90,0,0])cylinder(h=8,d=2,$fn=20);

  }
  translate([-45,-33,(touchH-60)/2])cube([90,30,60]);
}
module coverRing(){
  difference(){
    translate([-touchL/2,-3/2,0])cube([touchL,3,touchH]);
    translate([-(touchL-18)/2,-3/2-.1,9])cube([touchL-18,3+.2,touchH-18]);
    for(j=[-1,0,1])
      for(i=[0,1])
        translate([j*(touchL-6)/2,4,2.5+i*(touchH-5)])rotate([90,0,0])cylinder(h=8,d=2,$fn=20);
    translate([(touchL-24)/2,-3/2-.1,(touchH-25)/2])cube([15,3.2,25]);
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


module sensorC(){
  difference(){
    union(){
      translate([0,0,0])cube([53,5,25],center=true);
      for(i=[0,1])mirror([i,0,0])translate([-20,13,-5])cube([8+2,20+4,11+4],center=true);
    }

    translate([0,-2,0])cube([40,5,21],center=true);
    for(i=[0,1])mirror([i,0,0])translate([-20,13+2-5,-5])translate([.75,-2,0])cube([8.6,20+10,11],center=true);
    for(i=[-1,1])translate([i*22.75,-10,5])rotate([-90,0,0])cylinder(h=14,d=4.5,$fn=30);
    *translate([0,-12,5])rotate([-90,0,0])cylinder(h=27,d=15,$fn=30); //d=15
    translate([0,0,-7.5])cube([26,6,12],center=true);
  }
  difference(){
    translate([0,0,-6.5])cube([30,5,12],center=true);
    translate([0,0,-7.5])cube([26,6,12],center=true);
  }
}


cableCL = 130; //min 35
cableCLbase = 30;
innerD = 9;
innerDbase= 18;
module cableCoverHalf() {
  difference(){
    union(){
       cylinder(h=cableCLbase+3,d=innerDbase+5,$fn=50);
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
  for(i=[0,1])mirror([i,0,0])
  translate([innerD/2+2+5,1,cableCL-5])
  difference(){
    union(){
      translate([-2.5,0,0])cube([5,2,10],center=true);
      rotate([90,0,0])cylinder(h=2,d=10,$fn=80,center=true);
    }
    rotate([90,0,0])cylinder(h=3,d=3.5,$fn=30,center=true);
  }
}

boxL = touchL+11;
boxH = touchH+11;
boxD = 80;
module box(){
  difference(){
    translate([0,0,boxH/2])cube([boxL,boxD,boxH],center=true);
    translate([0,-2,boxH/2])cube([touchL+1,boxD,touchH+1],center=true);
    
    //touchscreen
    //outer frame is asimetric
    translate([0,boxD/2-1,boxH/2+1.5])cube([touchL-13,4,touchH-17],center=true);
    //screws
    for(j=[-1,0,1])
      for(i=[0,1])
        translate([j*(touchL-6)/2,boxD/2+touchD/2,5+i*(touchH-5)+3])rotate([90,0,0])cylinder(h=8,d=2,$fn=20);
    
    //M3 screws for cover
    for(i=[0,1])mirror([i,0,0])
      translate([boxL/2-2.5,-boxD/2+6,boxH/2+5])rotate([0,90,0])cylinder(h=6,d=3.4,$fn=20,center=true);
    //cables
    translate([touchL/2-35,boxD/2-2-22,boxH-2.5])cylinder(h=6,d=innerDbase+5.5,$fn=60,center=true);
    //holes for plate
    translate([boxL/2-5.5,-boxD/2-2.5,5])cube([6,55,9]);
    translate([boxL/2-6,-12,14]){
      for(i=[-1,1])translate([0,i*22.75,18])rotate([0,90,0])cylinder(h=7,d=4.5,$fn=30);
      translate([0,0,18])rotate([-90,0,0])rotate([0,90,0])cylinder(h=7,d=8,$fn=30); //d=15
    }
  }
}

module cover(){
  translate([0,-3,boxH/2])cube([boxL,5,boxH],center=true);
  translate([0,.5,touchH/2+5.5])cube([touchL,2,touchH],center=true);
  for(i=[0,1])mirror([i,0,0])
    translate([boxL/2-8,6,boxH/2+5])
    difference() {
      cube([5,10,10],center=true);
      translate([1.3,0,0])
      rotate([30,0,0])rotate([0,90,0])cylinder(h=2.6,d=6.4,$fn=6,center=true); //M3 nut
      rotate([0,90,0])cylinder(h=10,d=3.4,$fn=20,center=true); //M3 screw
    }
}



////show
translate([touchL/2-35,boxD/2-2-22,boxH-4.1+0]){
  cableCoverHalf();
  rotate([0,0,180])cableCoverHalf();
}
box();
translate([0,-boxD/2-20,0])cover();


color("black")
translate([0,+boxD/2-touchD-.5,5.5])touchscreen();
*translate([0,+boxD/2-touchD-6,5.5])coverRing();

translate([(touchL+11)/2-6.5,-12,14])
rotate([0,0,-90]) plate();

translate([(touchL+11)/2+2.5,-12,14+13])
rotate([0,0,-90]) sensorC();


// //to print
//translate([0,-boxH/2,boxD/2])rotate([-90,0,0])box();
//translate([0,boxH/2,6])rotate([90,0,0])cover();
//translate([0,cableCL/2,0])rotate([90,0,0])cableCoverHalf();
//rotate([90,0,0])sensorC();