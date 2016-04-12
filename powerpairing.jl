# This function is agnostic to the length of each element in pairings,
# i.e. it can take either two-team or BP.
function runpairings!(points, pairings, strengths)
    for pairing in pairings
        teams_ordered = sort([pairing...], by=t->strengths[t])
        for (i, team) in enumerate(teams_ordered)
            points[team] += i - 1
        end
    end
end

function showpairings(pairings)
    for pairing in pairings
        println(join(map(string, pairing), ", "))
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

function getrankedteams(brackets)
    teams = vcat([sort(bracket) for bracket in reverse(brackets)]...)
end

function simulatetournament(pairingfunction::Function, strengths, nrounds; verbosity=0)
    points = zeros(Int, length(strengths))
    brackets = Vector{Vector{Int64}}(1)
    brackets[1] = collect(1:length(strengths))
    for i in 1:nrounds
        pairings = pairingfunction(brackets)
        if verbosity > 1
            println("\nPairings for round $i:")
            showpairings(pairings)
        end
        runpairings!(points, pairings, strengths)
        brackets = groupbrackets(points)
        if verbosity > 0
            println("\nAfter round $i:")
            showbrackets(brackets)
        end
    end
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


# Functions that generate pairings.
# All of them take brackets, which is a vector of vectors, each list being teams in a bracket,
# and return a vector of tuples, each tuple being a pairing.

pairrandom2(brackets) = pairrandom(brackets, 2)
pairrandom4(brackets) = pairrandom(brackets, 4)
pairpower2(brackets) = pairpower(brackets, 2)
pairpower4(brackets) = pairpower(brackets, 4)

function pairrandom(brackets, roomsize)
    teams = vcat(brackets...)
    shuffled = shuffle(teams)
    return collect(zip([shuffled[i:roomsize:end] for i in 1:roomsize]...))
end

function pairpower(brackets, roomsize)
    pairings = []
    pushup = []
    for teams in brackets # do lowest bracket first (easier to iterate with pull-ups this way)
        
        # If there aren't enough teams to pair, add all teams to pushup and skip bracket
        if length(teams) + length(pushup) < roomsize
            append!(pushup, teams)
            continue # skip bracket if there aren't enough teams to pair
        end

        # Set aside random team(s) to push into next bracket up
        nodd = (length(teams) + length(pushup)) % roomsize
        @assert nodd <= length(teams)
        pushup_indices = sort(randperm(length(teams))[1:nodd])
        next_pushup = teams[pushup_indices]
        deleteat!(teams, pushup_indices)       
        
        # Add teams pulled up from next bracket down
        append!(teams, pushup)        
        pushup = next_pushup
        
        # Pair the teams in the now-adjusted bracket
        # Note: As per WUDC rules, the entire adjusted bracket is paired together, i.e. if 
        # there are multiple pull-up teams, they aren't necessarily all in the same room.
        @assert length(teams) % roomsize == 0
        shuffled = shuffle(teams) # shuffle again to randomize pull-up team position
        pairs = collect(zip([shuffled[i:roomsize:end] for i in 1:roomsize]...))
        append!(pairings, pairs)
    end
    @assert length(pushup) == 0 # there should not be a pull-up left over at the end
    return pairings
end
