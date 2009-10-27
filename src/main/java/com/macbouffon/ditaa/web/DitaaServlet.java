package com.macbouffon.ditaa.web;

import java.awt.image.RenderedImage;
import java.io.IOException;
import javax.imageio.ImageIO;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.stathissideris.ascii2image.core.ConversionOptions;
import org.stathissideris.ascii2image.graphics.BitmapRenderer;
import org.stathissideris.ascii2image.graphics.Diagram;
import org.stathissideris.ascii2image.text.TextGrid;

/**
 *
 * @author mlecarme
 */
public class DitaaServlet extends HttpServlet {
   public static final String NOANTIALIAS = "no-antialias";
   public static final String TABS = "tabs";
   public static final String NOSHADOW = "no-shadows";
   public static final String SCALE = "scale";
   public static final String ROUNDCORNERS = "round-corners";
   public static final String NOSEPARATIONS = "no-separation";
   public static final String DITAA = "ditaa";

   private boolean parseBoolean(String bool) {
       if(bool != null) {
           if(bool.toLowerCase().equals("true"))
               return true;
           if(bool.equals("1"))
               return true;
       }
       return false;
   }
    /** 
     * Processes requests for both HTTP <code>GET</code> and <code>POST</code> methods.
     * @param request servlet request
     * @param response servlet response
     * @throws ServletException if a servlet-specific error occurs
     * @throws IOException if an I/O error occurs
     */
    protected void processRequest(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {
        ConversionOptions options = new ConversionOptions();
        options.renderingOptions.setAntialias(! parseBoolean(request.getParameter(NOANTIALIAS)));
        options.renderingOptions.setDropShadows(! parseBoolean(request.getParameter(NOSHADOW)));
        options.processingOptions.setPerformSeparationOfCommonEdges(! parseBoolean(request.getParameter(NOSEPARATIONS)));
        if(request.getParameter(SCALE) != null)
            options.renderingOptions.setScale(Float.parseFloat(request.getParameter(SCALE)));
        else
            options.renderingOptions.setScale(1.0f);
        options.processingOptions.setAllCornersAreRound(parseBoolean(request.getParameter(ROUNDCORNERS)));
        boolean tabs = parseBoolean(request.getParameter(TABS));
        boolean noSeparations = parseBoolean(request.getParameter(NOSEPARATIONS));
        TextGrid grid = new TextGrid();
        String ditaa;
        if(request.getParameter(DITAA) != null)
            ditaa = request.getParameter(DITAA);
        else
            ditaa = "+-------------+\n" +
                    "| cBLU        |\n" +
                    "| Ditaa       |\n" +
                    "|    +--------+\n" +
                    "|    |cPNK    |\n" +
                    "|    | Test   |\n" +
                    "|    | servlet|\n" +
                    "+----+--------+\n";

        grid.initialiseWithText(ditaa, options.processingOptions);

        Diagram diagram = new Diagram(grid, options);

        RenderedImage image = BitmapRenderer.renderToImage(diagram, options.renderingOptions);
        response.setContentType("image/png");
        response.setHeader("Content-disposition", "inline; filename=ditaa.png");
        ImageIO.write(image, "png", response.getOutputStream());
    } 

    // <editor-fold defaultstate="collapsed" desc="HttpServlet methods. Click on the + sign on the left to edit the code.">
    /** 
     * Handles the HTTP <code>GET</code> method.
     * @param request servlet request
     * @param response servlet response
     * @throws ServletException if a servlet-specific error occurs
     * @throws IOException if an I/O error occurs
     */
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {
        processRequest(request, response);
    } 

    /** 
     * Handles the HTTP <code>POST</code> method.
     * @param request servlet request
     * @param response servlet response
     * @throws ServletException if a servlet-specific error occurs
     * @throws IOException if an I/O error occurs
     */
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {
        processRequest(request, response);
    }

    /** 
     * Returns a short description of the servlet.
     * @return a String containing servlet description
     */
    @Override
    public String getServletInfo() {
        return "Short description";
    }// </editor-fold>

}
