from gmplot import gmplot

latitude_list = [ 5.5952954, 5.5935851, 5.5999059, 5.5999059, 5.5999059, 5.6026555 ]
longitude_list = [ -0.2237016, -0.2235987, -0.2286033,-0.2265648,-0.2265648,-0.2265648]


gmap = gmplot.GoogleMapPlotter(5.5988617, -0.2265554, 15, map_type='SATELLITE')
gmap.apikey = "AIzaSyDkw3a_XLgmpbUFB1yuuNj3o5cFlhP7HCo"

gmap.scatter( latitude_list, longitude_list, 'blue',size = 40, marker = True)

# draw polygon
gmap.polygon(latitude_list, longitude_list,color = 'cornflowerblue')


gmap.draw( "map15.html" )
