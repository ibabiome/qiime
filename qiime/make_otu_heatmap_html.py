#!/usr/bin/env python
#file make_otu_heatmap_html.py

from __future__ import division

__author__ = "Jesse Stombaugh"
__copyright__ = "Copyright 2011, The QIIME Project" 
__credits__ = ["Jesse Stombaugh", "Jose Carlos Clemente Litran"] #remember to add yourself
__license__ = "GPL"
__version__ = "1.6.0"
__maintainer__ = "Jesse Stombaugh"
__email__ = "jesse.stombaugh@colorado.edu"
__status__ = "Release"


from numpy import array,concatenate,asarray,transpose,log,invert,asarray,\
    float32,float64, minimum, inf
from cogent.parse.table import SeparatorFormatParser
from optparse import OptionParser
from qiime.util import MissingFileError
import os
from qiime.filter import filter_otus_from_otu_table
from biom.parse import parse_biom_table

def make_html_doc(js_filename):
    """Create the basic framework for the OTU table heatmap"""
    html_script = \
    r'''
    <html>
    <head>
    	<script type="text/javascript" src="js/overlib.js"></script>
        <script type="text/javascript" src="%s"></script>
    	<script type="text/javascript" src="js/otu_count_display.js"></script>
    	<script type="text/javascript" src="./js/jquery.js"></script>
    	<script type="text/javascript" src="./js/jquery.tablednd_0_5.js"></script>
        <script type="text/javascript">

    
        $(document).ready(function() {
    
        	$('#otu_table_body').tableDnD({
        		onDragStart: function(table, new_row) {
        			if (row==new_row.parentNode.rowIndex && is_selected==1){
        				change_sel_row=1;
        			}else{
        				old_row=new_row.parentNode.rowIndex;
        				change_sel_row=0;
        			}
        		},
        		onDrop: function(table, new_row) {
        			if (change_sel_row==1){
        				row=new_row.rowIndex;
        			}else if(old_row<row && new_row.rowIndex>row){
        				row=row-1;
        			}else if(old_row>row && new_row.rowIndex<row){
        				row=row+1;
        			}
        		},
            	dragHandle: "dragHandle"
        	});
            var otu_cutoff=document.getElementById("otu_count_cutoff");
            otu_cutoff.value=otu_num_cutoff;    
        });
        </script>
    	<style type="text/css">
    	    th.rotate{ 
    			white-space : nowrap;
    			-webkit-transform: rotate(-90deg) translate(20px, 0px); 
    			-moz-transform: rotate(-90deg) translate(20px, 0px);	
    			font-family:arial;
    			font-size:9px;
    		}
    		th.lineage{ 
        	    white-space : nowrap;
        	    text-align:left;
        	    font-family:arial;
        	    font-size:10px;
        	    font-weight: bolder;
        	}
        	td.dragHandle{ 
            	white-space : nowrap;
            	text-align:left;
            	font-family:arial;
            	font-size:10px;
            	font-weight: bolder;
        	}
        	td{ 
            	white-space : nowrap;
            	font-family:arial;
            	font-size:10px;
            	text-align:center;
            	font-weight: bolder;
        	}       
        	table{ 
            	border-spacing: 0;
            	text-align:center;
        	}
        	p{
            		text-align:left;
            		font-weight: normal;
        	}    
    	</style>
    </head>
    <body>
    	<p>
    		Filter by Counts per OTU: <input type="text" id="otu_count_cutoff" value="">
    		<input type="button" onclick="javascript:create_OTU_intervals();" value="Sample ID">
    		<input type="button" onclick="javascript:write_taxon_heatmap();" value="Taxonomy">
    	</p>
    	<br><br><br><br><br><br>
    	<table id='otu_table_html'>
    		<thead id='otu_table_head'>
    		</thead>
    		<tbody id='otu_table_body'>
    		<tr><td class="dragHandle"></td>
    		</tr>
    		<tr><td class="dragHandle"></td>
    		</tr>
    		</tbody>
    	</table>

    </body>
    </html>''' % (js_filename)
    return html_script

#def create_javascript_array(rows, use_floats=False):
def create_javascript_array(otu_table, use_floats=False):
    """Convert the OTU table counts into a javascript array"""
    
    js_array='\
    var OTU_table=new Array();\n\
    var i=0;\n\
    for (i==0;i<%i;i++) {\n\
    OTU_table[i]=new Array();}\n' % (len(otu_table.SampleIds) + 2)

    #0 ['#OTU ID', 'OTU2', 'OTU3']
    #1 ['Sample1', 1, 2]
    #2 ['Sample2', 5, 4]
    #3 ['Consensus Lineage', 'Archaea', 'Bacteria']

    # OTU ids first
    js_array += "OTU_table[0][0]='#OTU ID';\n"
    for (idx, otu_id) in enumerate(otu_table.ObservationIds):
        js_array += "OTU_table[0][%i]='%s';\n" % (idx+1, otu_id)

    # Sample ids and values in the table
    i = 1
    for (sam_val, sam_id, meta) in otu_table.iterSamples():
        js_array += "OTU_table[%i][0]='%s';\n" % (i, sam_id)
        for (idx, v) in enumerate(sam_val):
            if use_floats:
                js_array += "OTU_table[%i][%i]=%.4f;\n" % (i, idx+1, float(v))
            else:
                # don't quite understand why int(float(v)), rather than int(v)
                js_array += "OTU_table[%i][%i]=%d;\n" % (i, idx+1, int(float(v)))
        i += 1

    # Consensus lineages for each OTU
    last_idx = len(otu_table.SampleIds) + 1
    js_array += "OTU_table[%i][0]='Consensus Lineage';\n" % last_idx
    i = 1
    for (otu_val, otu_id, meta) in otu_table.iterObservations():
        # meta['taxonomy'] might need to be print as ";".join()
        js_array+="OTU_table[%i][%i]='%s';\n" % (last_idx, i, ";".join(meta['taxonomy']).strip('"'))
        i += 1

    ### previous code
    #for i in range(len(rows)):
    #    for j in range(len(rows[i])):
    #        if i==0 or j==0 or i==len(rows)-1:
    #            js_array+="OTU_table[%i][%i]='%s';\n" % (i,j,(rows[i][j]))
    #        else:
    #            if use_floats:
    #                js_array+="OTU_table[%i][%i]=%.4f;\n" % (i,j,float(rows[i][j]))
    #            else:
    #                js_array+="OTU_table[%i][%i]=%d;\n" % (i,j,int(float(rows[i][j])))
            
    return js_array

#def filter_by_otu_hits(num_otu_hits,data):
def filter_by_otu_hits(num_otu_hits, otu_table):
    """Filter the OTU table by the number of otus per sample"""

    #col_header,row_header,otu_table,lineages=data['otu_counts']

    #lineages_update=[]
    #for i in range(len(lineages)):
    #    new_lineages=''
    #    for j in lineages[i]:
    #        new_lineages+=j.strip('"')+';'
    #    lineages_update.append(new_lineages)
    #lineages_update=array(lineages_update)
    # Equivalent to the line below, but we don't need to deal with it here
    #lineages_update = array([';'.join(l).strip('"') for l in lineages])

    # Don't care about headers here, deal with it in create_javascript_array
    #rows_filtered=[]

    #row_head=concatenate((['#OTU ID'],col_header))
    #lineage_head=array(['Consensus Lineage'])
    #row_head2=concatenate((row_head,lineage_head))
    #rows_filtered.append(row_head2)

    # Filter out rows with sum > num_otu_hits
    new_otu_table = filter_otus_from_otu_table(otu_table, otu_table.ObservationIds,
                                               num_otu_hits, inf,0,inf)

    return new_otu_table

    #for i in range(len(otu_table)):
    #    if otu_table[i].sum()>num_otu_hits:
    #        row_head_otu_count=concatenate(([row_header[i]],otu_table[i],[lineages_update[i]]))
    #
    #        rows_filtered.append(row_head_otu_count)

    # This is returning the new otu table transposed, why?
    #rows_filtered=array(rows_filtered) 
    #trans_rows_filtered=rows_filtered.transpose()
    #return trans_rows_filtered

# Never used??    
def line_converter():
    """Converts line elements into int's if possible"""
    def callable(line):
        new = []
        append = new.append
        for element in line:
            try:
                append(int(element))
            except ValueError:
                append(element)
        return new
    return callable

#def get_log_transform(data, eps=None):
def get_log_transform(otu_table, eps=None):
    """ This function and the one in make_otu_heatmap.py are essentially the same except
    the non-negative transform at the end of this function. Dan Knights suggests this might
    be due to this script not being able to handle negative values, hence the transform.
    """
    # ensure data are floats
    #data = asarray(data,dtype=float64)
    #if not data.dtype == float32 and not data.dtype == float64:
    #    data = asarray(data,dtype=float32)

    # set all zero entries to a small value
    #zero_entries = data == 0
    #if eps is None:
    #    smallest_nonzero = (data[invert(zero_entries)]).min()
    #    eps = smallest_nonzero/2
    #data[zero_entries] = eps
    #data = log(data)
    # set minimum to 0
    #data = data - (data).min()
    #return data

    # explicit conversion to float: transform
    def f(s_v, s_id, s_md):
        return float64(s_v)
    float_otu_table = otu_table.transformSamples(f)

    if eps is None:
        # get the minimum among nonzero entries and divide by two
        eps = inf
        for (obs, sam) in float_otu_table.nonzero():
            eps = minimum(eps, float_otu_table.getValueByIds(obs,sam))
        if eps == inf:
            raise ValueError('All values in the OTU table are zero!')
    
    # set zero entries to eps/2 using a transform

    def g2(x):
        return [i if i !=0 else eps/2 for i in x]

    # do we have map in OTU object?
    g = lambda x : x if (x != 0) else eps/2
    def g_m(s_v, s_id, s_md):
        return asarray(map(g,s_v))

    eps_otu_table = float_otu_table.transformSamples(g_m)

    # take log of all values with transform
    def h(s_v, s_id, s_md):
        return log(s_v)
    log_otu_table = eps_otu_table.transformSamples(h)

    # one more transform
    min_val = inf
    for val in log_otu_table.iterSampleData():
        min_val = minimum(min_val, val.min())
    def i(s_v, s_id, s_md):
        return s_v - min_val

    res_otu_table = log_otu_table.transformSamples(i)

    return res_otu_table

#def get_otu_counts(fpath, data):
# data is being passed but not used
def get_otu_counts(fpath):
    """Reads the OTU table file into memory"""

    try:
        otu_table = parse_biom_table(open(fpath,'U'))
    except (TypeError, IOError):
        raise MissingFileError, 'OTU table file required for this analysis'

    if (otu_table.ObservationMetadata is None or
        otu_table.ObservationMetadata[0]['taxonomy'] is None):
        raise ValueError, '\n\nThe lineages are missing from the OTU table. Make sure you included the lineages for the OTUs in your OTU table. \n'

    return otu_table

#def generate_heatmap_plots(options, data, dir_path, js_dir_path,
#                        filename,fractional_values=False):
def generate_heatmap_plots(num_otu_hits, otu_table, otu_sort, sample_sort, dir_path,
                           js_dir_path, filename,fractional_values=False):
    """Generate HTML heatmap and javascript array for OTU counts"""

    #Filter by number of OTU hits
    # rows come transposed in the original code
    #rows=filter_by_otu_hits(options.num_otu_hits, data)
    filtered_otu_table = filter_by_otu_hits(num_otu_hits, otu_table)

    # This sorts the otus by the tree supplied
    #if data['otu_order']:
    #    new_otu_table=[]
    #    tran_rows=rows.transpose()
    #
    #    new_otu_table.append(tran_rows[0])
    #    for i in data['otu_order']:
    #        for j in tran_rows:
    #            if i==j[0]:
    #                new_otu_table.append(j)
    #    rows= asarray(new_otu_table).transpose()
      
    if otu_sort:
        # Since the BIOM object comes back with fewer Observation_ids, we need to 
        # remove those from the original sort_order
        actual_observations=filtered_otu_table.ObservationIds
        new_otu_sort_order=[]
        for i in otu_sort:
            if i in actual_observations:
                new_otu_sort_order.append(i)
                
        filtered_otu_table = filtered_otu_table.sortObservationOrder(new_otu_sort_order)

    # This sorts the samples by the order supplied
    #if data['sample_order']:
    #    new_otu_table=[]
    #    new_otu_table.append(rows[0])
    #    for i in data['sample_order']:
    #        for j in rows:
    #            if i==j[0]:
    #                new_otu_table.append(j)
    #    # last row is lineages
    #    new_otu_table.append(rows[-1])
    #    rows= asarray(new_otu_table)
    if sample_sort:
        # Since the BIOM object may come back with fewer Sampleids, we need to 
        # remove those from the original sample_sort
        actual_samples=filtered_otu_table.SampleIds
        new_sample_sort_order=[]
        for i in sample_sort:
            if i in actual_samples:
                new_sample_sort_order.append(i)
                
        filtered_otu_table = filtered_otu_table.sortSampleOrder(new_sample_sort_order)
        
    #Convert OTU counts into a javascript array
    js_array=create_javascript_array(filtered_otu_table, fractional_values)

    #Write otu filter number
    js_otu_cutoff='var otu_num_cutoff=%d;' % num_otu_hits
    
    #Write js array to file
    js_filename=os.path.join(js_dir_path,filename)+'.js'
    jsfile = open(js_filename,'w')
    jsfile.write(js_otu_cutoff)
    jsfile.write(js_array)
    jsfile.close()

    #Write html file
    html_filename=os.path.join(dir_path,filename)+'.html'
    js_file_location='js/'+filename+'.js'
    table_html=make_html_doc(js_file_location)
    ofile = open(html_filename,'w')
    ofile.write(table_html)
    ofile.close()
