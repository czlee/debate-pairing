using Gadfly

nrounds = 8
wins_to_break = 6
probnotbreak(rank) = sum([(1-rank)^i*rank^(nrounds-i)*binomial(nrounds,i) for i in 0:wins_to_break-1])
myplot = plot(probnotbreak, 0, 0.4)
draw(SVG("plot.svg", 6inch, 4.5inch), myplot)