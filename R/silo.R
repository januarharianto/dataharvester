#' Download from SILO database
#'
#' @param layer `r params(layer)`
#' @param bounding_box `r params(bounding_box)`
#' @param out_path `r params(out_path)`
#' @param years `r params(years)`
#' @param format_out Exported file format. Only `"tif"` is currently available.
#'   Defaults to `"tif"`
#' @param delete_temp Delete any temporary files that were created. Defaults to
#'   `FALSE`
#'
#' @return a list of filenames (after files have been downloaded or processed)
#' @export
download_silo <- function(layer,
                          bounding_box,
                          out_path,
                          years,
                          format_out = "tif",
                          delete_temp = FALSE) {
  # Import module
  silo <- harvester_module("getdata_silo")
  # make sure years is integer
  years <- as.integer(years)
  # Iteration happens outside of the main function
  layers <- layer
  out <- NULL
  for (i in layers) {
    i_path <- paste0(out_path, "silo_", i)
    ref <- silo$get_SILO_raster(
      i,
      years,
      out_path,
      bounding_box,
      format_out,
      delete_temp
    )
    out <- append(out, ref)
  }
  class(out) <- append(class(out), "rasterPath")
  return(out)
}
