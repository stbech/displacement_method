file_main = file . '.gpd'
file_add = file . '_add.gpd'

set size 1,1 

# Grenzen des Systems
#reset
#stat file_main i 0 u 1:2 nooutput

#set yrange[*:*] reverse
set yrange [*:*] reverse noextend
set xrange [*:*] noextend
#set yrange[(STATS_max_y+padding):(STATS_min_y-padding)] noextend # max. y-Werte zzgl. Zuschlag
#set xrange[*<(STATS_min_x-padding):(STATS_max_x+padding)<*] noextend

set offset padding ,padding ,padding ,padding


#set size ratio -1
set size ratio -1#1,1 
set angles degrees


set xlabel 'x [m]'
set ylabel 'y [m]'

# Befehle

set style arrow 100 backhead filled lc rgb 'orange'
set style arrow 101 nohead lc rgb 'orange'

set style arrow 102 backhead filled lc rgb 'red'
set style arrow 103 backhead filled lc rgb 'red' size graph 0.008,15 fixed

set style arrow 104 nohead lc rgb 'black' dt 2

x_plot(x_l, x, alpha, val, factor) = x_l + cos(alpha)*x + sin(alpha)*factor*val
y_plot(y_l, x, alpha, val, factor) = y_l - sin(alpha)*x + cos(alpha)*factor*val

x_vec(x_0, val, alpha) = val > 0 ? x_0 + offset*cos(alpha) : x_0 + (offset - val*factor_L)*cos(alpha)
y_vec(y_0, val, alpha) = val > 0 ? y_0 - offset*sin(alpha) : y_0 - (offset - val*factor_L)*sin(alpha)
x_load(x_0, val, alpha, factor_o) = val > 0 ? x_0 + (offset*factor_o + val*factor_L)*cos(alpha) : x_0 + (offset*factor_o - val*factor_L)*cos(alpha)
y_load(y_0, val, alpha, factor_o) = val > 0 ? y_0 - (offset*factor_o + val*factor_L)*sin(alpha) : y_0 - (offset*factor_o - val*factor_L)*sin(alpha)
dx_load(alpha, alpha_bar, length, val_l, val_r) =  cos(alpha_bar)*length + sin(alpha)*(val_l-val_r)*factor_L
dy_load(alpha, alpha_bar, length, val_l, val_r) = -sin(alpha_bar)*length + cos(alpha)*(val_l-val_r)*factor_L

min_max(min, max) = sprintf('{/*%fmin: %.3f, max: %.3f}', factor_t, min, max)
comb_min(min, max) = sprintf('{/*%fmin: %.3f,&{ max: %.3f}}', factor_t, min, max)
comb_max(min, max) = sprintf('{/*%f&{min: %.3f,} max: %.3f}', factor_t, min, max)
load(val) = sprintf('{/*%f %.3f}', factor_t, val)

