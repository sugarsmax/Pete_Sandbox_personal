global F G k P N r wi maxzdstep maxzdramp;
maxzdramp=[0,0]; maxzdstep=[0,0];
F=[0 2 0 0 0; -.1 -.35 .1 .1 .75; 0 0 0 2 0; .4 .4 -.4 -1.4 0; 0 -.03 0 0 -1];
G=[0 0 0 0 1]';
H2=[0 0 1 0 0];
H3=[.5 0.5 0 0 0];
Ht=[-.2 -.2 .2 .2 0];
%F(2,:)=2*F(2,:);

p1=-1.01+.9158*i; p3=-1.5+1.395*i; p5=-3.0;
p2=real(p1)-imag(p1)*i; p4=real(p3)-imag(p3)*i;
P=[p1 p2 p3 p4 p5];
k = acker(F,G,P);
N=1 /(H3 *inv(-F+(G*k))*G);
x0=[0 0 0 0 0]';
figure(1); clf; hold on;
[t,x]=ode45(@stepinput,[0,20],x0);
pos=H3 *x' ; ten=Ht*x' ;
plot(t,pos);
Mp=sprintf('Mp = %4.3f %%',(max(pos)-1)*100);
grid; xlabel('Time (msec)'); ylabel('Position 0 (1e-5 m)');
title ('Maxfield - Tape Drive Position - Step Input - J1=.5J1');
text(2.5, 1.1, Mp);
hold off;
figure(2); clf; hold on;
plot(t,ten);
grid; xlabel('Time (msec)'); ylabel('Tension T (N)');
title ('Maxfield - Tape Drive Tension - Step Input - J1=.5J1'); hold off;
figure(3); clf; hold on;
[t2,x2] = ode45(@rampinput,[0,20],x0);
pos2=H3*x2'; ten2=Ht*x2';
plot(t2,pos2,'g');
plot(t2,t2,'k');
plot(t2,(t2-pos2')* 10,'y');
grid; xlabel('Time (msec)'); ylabel('Position 0 (1e-5 m)');
title ('Maxfield - Tape Drive Position - Ramp Input - J1=.5J1');
text(2, 11,'Error * 10'); hold off;
figure(4); clf; hold on;
plot(t2,ten2);
grid; xlabel('Time (msec)'); ylabel('Tension T (N)');
title ('Maxfield - Tape Drive Tension - Ramp Input - J1=.5J1'); hold off;

%% Local functions for ODE solver
function xdot = stepinput(t, x)
    global F G k N;
    r = 1;              % Step reference
    u = N*r - k*x;      % Control input with state feedback
    xdot = F*x + G*u;   % State derivative
end

function xdot = rampinput(t, x)
    global F G k N;
    r = t;              % Ramp reference
    u = N*r - k*x;      % Control input with state feedback
    xdot = F*x + G*u;   % State derivative
end

function zdot = tapd(t, z)
    % Step input with control saturation and disturbance
    global F G k N maxzdstep;
    r = 1;                      % Step reference
    w = [0 0 0 0 0]';           % Disturbance vector
    u = N*r - k*z;              % Control input
    % Saturate control input to [-2, 2]
    if u < -2
        u = -2;
    end
    if u > 2
        u = 2;
    end
    zdot = F*z + G*u + w;       % State derivative with disturbance
    % Track maximum zdot values
    if zdot(2) < maxzdstep(1)
        maxzdstep(1) = zdot(2);
    end
    if zdot(4) < maxzdstep(2)
        maxzdstep(2) = zdot(4);
    end
end
