using PyPlot

ntournaments = 100
nteams = 80
nrounds = 4

function runpairings!(points, pairings, strengths)
    for (t1, t2) in pairings
        if strengths[t2] > strengths[t1]
            points[t2] += 1
        else
            points[t1] += 1
        end
    end
end

function showbrackets(brackets)
    for (p, teams) in reverse(collect(enumerate(brackets)))
        teams_str = join(map(string, teams), " ")
        println("$(p-1): $teams_str")
    end
end

function groupbrackets(points)
    maxpoints = maximum(points)
    brackets = [[] for p in 0:maxpoints]
    for (t, p) in enumerate(points)
        push!(brackets[p+1], t)
    end
    return brackets
end

function pairrandom(brackets)
    teams = vcat(brackets...)
    shuffled = shuffle(teams)
    return collect(zip(shuffled[1:end÷2], shuffled[end÷2+1:end]))
end

function pairpower(brackets)
    pairings = []
    odd = -1
    for teams in brackets
        if odd != -1 # pull-up team
            push!(teams, odd)
            odd = -1
        end
        shuffled = shuffle(teams)
        if length(teams) % 2 == 1
            odd = pop!(teams)
        end
        pairs = collect(zip(shuffled[1:end÷2], shuffled[end÷2+1:end]))
        append!(pairings, pairs)
    end
    @assert odd == -1 # there should not be a pull-up left over at the end
    return pairings
end

function getrankedteams(brackets)
    teams = vcat([sort(bracket) for bracket in reverse(brackets)]...)
end

function simulatetournament(pairingfunction::Function, strengths, nrounds)
    points = zeros(Int, length(strengths))
    brackets = Vector{Vector{Int64}}(1)
    brackets[1] = collect(1:length(strengths))
    for i in 1:nrounds
        pairings = pairingfunction(brackets)
        runpairings!(points, pairings, strengths)
        brackets = groupbrackets(points)
    end
    showbrackets(brackets)
    return brackets
end

function simulatemanytournaments(pairingfunction::Function, ntournaments::Int, nteams::Int, nrounds::Int)
    strengths = collect(nteams:-1:1)
    positions = Any[Int[] for t in strengths]
    for i in 1:ntournaments
        brackets = simulatetournament(pairingfunction, strengths, nrounds)
        rankedteams = getrankedteams(brackets)
        for (pos, team) in enumerate(rankedteams)
            push!(positions[team], pos)
        end
    end
    return positions
end

powerpositions = simulatemanytournaments(pairpower, ntournaments, nteams, nrounds)
powerplot = boxplot(powerpositions)
show()

clf()
randompositions = simulatemanytournaments(pairrandom, ntournaments, nteams, nrounds)
randomplot = boxplot(randompositions)
show()
