%figure(5); clf;
%bode(F-G*k,G*N,H3,0,1);
%figure(6);
%orlocus(F-G*k,G*N,H3,0,1); %axis([-3.5 1 -2 2]);
%title ('Maxfield - Tape Drive Root Locus - w=0');
% Peter Maxfield
% MAE 326 - Tape Drive
% Step Input
function [zdot] = tapd(t,z);
global F G k P N r w maxzdstep;
r=1;
w=[0 0 0 0 01,;
u = -k*z + N*r;
if u<-2
u=-2; e
nd;
if u>2
u=2;
end;
zdot=F*z + G*u + w;
if zdot(2)<maxzdstep(1)
maxzdstep(1)=zdot(2);
end
if zdot(4)<maxzdstep(2)
maxzdstep(2)=zdot(4);
end