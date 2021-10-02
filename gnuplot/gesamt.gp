reset
# Text darstellen, Maßstab für System und Schnittgröße

file = 'gesamt_2.gpd'

schnittgroesse = 'V'
lf = '1'

factor_s = 0.2      # Größe der Auflager
factor_l = 0.3      # Abstand Text von Systemlinie
offset = 0.2
factor_L = 0.1
factor_N = 0.03     # Skalierung Normalkraft
factor_V = 0.03     # Skalierung Querkraft
factor_M = 0.03     # Skalierung Moment
factor_w = 0.03     # Skalierung Verformung

#TODO padding über leerzeichengetrennten String für jede Seite seperat einstellen
padding = 1         # Überstand von Systemlinie zum Rand
#-------------------------------------------------------------



#set terminal pdfcairo size 29.7cm,21cm fontscale 0.4
#set encoding iso_8859_1
#set output 'Moment.pdf'

set size 1,1 # 1,1 entspricht 127.0 mm x 88.9 mm

# Grenzen des Systems
stat file i 0 u 1:2 nooutput

set yrange[(STATS_max_y+padding):(STATS_min_y-padding)]     # max. y-Werte zzgl. Zuschlag
set xrange[(STATS_min_x-padding):(STATS_max_x+padding)]

set size ratio -1
set angles degrees


set xlabel 'x [m]'
set ylabel 'y [m]'

if (schnittgroesse eq 'w') {
    s = 3
    s_text = 'Verformung'
    factor = factor_w
} else {
    if (schnittgroesse eq 'M') {
        s = 2
        s_text = 'Moment'
        factor = factor_M
    } else {
        if (schnittgroesse eq 'V') {
            s = 1
            s_text = 'Querkraft'
            factor = factor_V
        } else {
            if (schnittgroesse eq 'N') {
                s = 0
                s_text = 'Normalkraft'
                factor = factor_N
            } else {
                print 'Fehler: Kuerzel fuer Schnittgroesse nicht erkannt!'
                exit
            }
        }
    }
}

set title s_text . ' infolge LF ' . lf left offset graph -0.5 font ",15"

# Linienfarbe abhängig vom Vorzeichen der Schnittgrößen
# RGB Definition: INT der Anteile von 0 bis 255
# eine gemeinsame Zahl: 65536 * int(r) + 256 * int(g) + int(b)
#color(y) = y >= 0 ? (255) : (255*65336)    # blau bzw. rot
#:(color($4))

#load 'include_command.gp'

set style arrow 100 backhead filled lc rgb 'orange'
set style arrow 101 nohead lc rgb 'orange'

x_plot( x_l, x, alpha, val, factor) = x_l + cos(alpha)*x + sin(alpha)*factor*val
y_plot( y_l, x, alpha, val, factor) = y_l - sin(alpha)*x + cos(alpha)*factor*val

#stats [0:1000] 'gesamt_2.gpd' i 2 u ($5) every:4::s # Wie null am Anfang und Ende ignorieren?

plot    file i 0 ev:2 w l lc rgb 'black' notitle, \
        '' i 0 ev:2::1  w l lc rgb 'black' dt 2 notitle, \
        file i 1 u ($1+factor_s*$3):($2+factor_s*$4) w l lc rgb 'black' notitle,\
        file i 2 u (x_plot($1, $3, $4, $5, factor)):(y_plot($2, $3, $4, $5, factor)) ev:4::s w l notitle lc rgb 'red', \
        'label.gpd' u ($1-sin($3)*factor_l):($2-cos($3)*factor_l):(sprintf("{/*0.5 %s}", strcol(4))):3  with labels rotate variable center notitle, \
        'load.gpd' i 0 u ($1+offset*cos($3)):($2-offset*sin($3)):(cos($3)*$4*factor_L):(-sin($3)*$4*factor_L) w vec notitle as 100, \
        '' i 0 u ($1+(offset*2+$4*factor_L)*cos($3)):($2-(offset*2+$4*factor_L)*sin($3)):4:($3 <= 0 ? $3+90 : $3-90) w labels notitle rotate variable center, \
        '' i 1 u ($1+(offset+$5*factor_L)*cos($3+90)):($2-(offset+$5*factor_L)*sin($3+90)):(cos($3)*$4 + sin($3)*($5-$6)*factor_L):(-sin($3)*$4 + cos($3)*($5-$6)*factor_L) w vec notitle as 101, \
        #'support.gpd' using ($1+factor_s*$3):($2+factor_s*$4) with lines notitle linetype rgb 'black' ,\

set terminal wxt #size 2000,1500  # Damit das Schreiben in die PDF beendet werden kann
refresh

#TODO gerade Linien brauchen die Vektor Größe am Anfang und Ende, dafür aber den Faktor nicht im Offset