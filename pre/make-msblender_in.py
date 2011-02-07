#!/usr/bin/python
import os 
import sys

usage_mesg = 'Usage: make-msblender_in.py <msblender_in.conf file>'

sp2hit = dict()
search_median = dict()
search_mad = dict()

search_engine_list = []
f_conf = open(sys.argv[1],'r')
for line in f_conf:
    if( line.startswith('#') ):
        continue
    tokens = line.strip().split()
    search_engine_name = tokens[0]
    search_engine_list.append( search_engine_name )

    score_list = []
    filename_hit_list = tokens[1]
    f_hit_list = open(filename_hit_list,'r')
    for line in f_hit_list:
        if( line.startswith('#') ):
            continue
        tokens = line.strip().split("\t")
        sp_id =  tokens[0]
        charge = tokens[1]
        pep_seq = tokens[4]
        prot_id = tokens[5]
        sp_pep_id = '%s.%s'%(sp_id,pep_seq)
        if( not sp2hit.has_key( sp_pep_id ) ):
            sp2hit[sp_pep_id] = dict()
        sp2hit[sp_pep_id][search_engine_name] = {'prot_id':prot_id, 'score': float(tokens[-1])}
        score_list.append(float(tokens[-1]))
    f_hit_list.close()

    idx_median = int( len(score_list)*0.5 )
    score_median = score_list[idx_median]
    score_mad = sorted([abs(x - score_median) for x in score_list])[idx_median]
    if( len(score_list) % 2 == 0 ):
        score_median = (score_list[idx_median-1] + score_list[idx_median])*0.5
        score_mad_list = sorted([abs(x - score_median) for x in score_list])
        score_mad = (score_mad_list[idx_median-1] + score_mad_list[idx_median])*0.5
    search_median[search_engine_name] = score_median
    search_mad[search_engine_name] = score_mad
f_conf.close()

search_engine_list = sorted(search_engine_list)

print "sp_pep_id\tdecoy\t%s"%("\t".join(["%s_score"%x for x in search_engine_list]))
for sp_pep_id in sorted(sp2hit.keys()):
    output_list = []
    is_decoy = 0
    for tmp_search_engine_name in search_engine_list:
        if( sp2hit[sp_pep_id].has_key( tmp_search_engine_name ) ):
            tmp_score = sp2hit[sp_pep_id][tmp_search_engine_name]['score']
            tmp_score = (tmp_score - search_median[tmp_search_engine_name])/search_mad[search_engine_name]
            output_list.append( "%f"%tmp_score )
            if( sp2hit[sp_pep_id][tmp_search_engine_name]['prot_id'].startswith('xf_') ):
                is_decoy = 1
        else:
            output_list.append( 'NA' )

    print "%s\t%d\t%s"%(sp_pep_id, is_decoy, '\t'.join(output_list) )
