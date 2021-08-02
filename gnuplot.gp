# Text darstellen, Maßstab für System und Schnittgröße

factor_s = 0.2      # Größe der Auflager
factor_M = 0.03     # 

schnittgroesse = 'M'



#set terminal pdf
#set encoding iso_8859_1
#set output 'Schnittgroessen.pdf'

set yrange[8:-3]
set xrange[-1:13]
set size ratio -1
set angles degrees


if (schnittgroesse eq 'M') {
    s = 2
} else {
    if (schnittgroesse eq 'V') {
        s = 1
    } else {
        s = 0
    }
}

# Linienfarbe abhängig vom Vorzeichen der Schnittgrößen
# RGB Definition: INT der Anteile von 0 bis 255
# eine gemeinsame Zahl: 65536 * int(r) + 256 * int(g) + int(b)
#color(y) = y >= 0 ? (255) : (255*65336)    # blau bzw. rot
#:(color($4))

#load 'include_command.gp'

plot    "system.gpd" every:2 with lines notitle lt rgb 'black', \
        '' every:2::1  with lines linetype rgb 'black' dashtype 2 notitle, \
        "schnittgroessen.gpd" using ($1+sin($3)*factor_M*$4):($2+cos($3)*factor_M*$4) every:3::s with lines notitle lt rgb 'red', \
        #'support.gpd' using ($1+factor_s*$3):($2+factor_s*$4) with lines notitle linetype rgb 'black' ,\

