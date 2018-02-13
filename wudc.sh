for i in {2..9}
do
    echo
    echo "Round $i - entropysq";
    ./wudc.py wudc2017 $i --cost entropysq -q --no-color;
    echo
    echo "Round $i - pvar";
    ./wudc.py wudc2017 $i --cost pvar -q --no-color;
    echo
    echo "Round $i - pvarsq";
    ./wudc.py wudc2017 $i --cost pvarsq -q --no-color;
    echo
    echo "Round $i - vanschelven";
    ./wudc.py wudc2017 $i --cost vanschelven -q --no-color;
done
