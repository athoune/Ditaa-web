package jargs.gnu;

import java.io.PrintStream;
import java.text.NumberFormat;
import java.text.ParseException;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Vector;
import java.util.Enumeration;
import java.util.Locale;

/**
 * Largely GNU-compatible command-line options parser. Has short (-v) and
 * long-form (--verbose) option support, and also allows options with
 * associated values (-d 2, --debug 2, --debug=2). Option processing
 * can be explicitly terminated by the argument '--'.
 *
 * @author Steve Purcell
 * @version $Revision: 1.5 $
 * @see jargs.examples.gnu.OptionTest
 */
public class CmdLineParser {

    /**
     * Base class for exceptions that may be thrown when options are parsed
     */
    public static abstract class OptionException extends Exception {
        OptionException(String msg) { super(msg); }
    }

    /**
     * Thrown when the parsed command-line contains an option that is not
     * recognised. <code>getMessage()</code> returns
     * an error string suitable for reporting the error to the user (in
     * English).
     */
    public static class UnknownOptionException extends OptionException {
        UnknownOptionException( String optionName ) {
            super("unknown option '" + optionName + "'");
            this.optionName = optionName;
        }

        /**
         * @return the name of the option that was unknown (e.g. "-u")
         */
        public String getOptionName() { return this.optionName; }
        private String optionName = null;
    }

    /**
     * Thrown when an illegal or missing value is given by the user for
     * an option that takes a value. <code>getMessage()</code> returns
     * an error string suitable for reporting the error to the user (in
     * English).
     */
    public static class IllegalOptionValueException extends OptionException {
        public IllegalOptionValueException( Option opt, String value ) {
            super("illegal value '" + value + "' for option -" +
                  opt.shortForm() + "/--" + opt.longForm());
            this.option = opt;
            this.value = value;
        }

        /**
         * @return the name of the option whose value was illegal (e.g. "-u")
         */
        public Option getOption() { return this.option; }

        /**
         * @return the illegal value
         */
        public String getValue() { return this.value; }
        private Option option;
        private String value;
    }

    /**
     * Representation of a command-line option
     */
    public static abstract class Option {

        protected Option( char shortForm, String longForm,
                          boolean wantsValue ) {
            if ( longForm == null )
                throw new IllegalArgumentException("null arg forms not allowed");
            this.shortForm = new String(new char[]{shortForm});
            this.longForm = longForm;
            this.wantsValue = wantsValue;
        }

        public String shortForm() { return this.shortForm; }

        public String longForm() { return this.longForm; }

        /**
         * Tells whether or not this option wants a value
         */
        public boolean wantsValue() { return this.wantsValue; }

        public final Object getValue( String arg, Locale locale )
            throws IllegalOptionValueException {
            if ( this.wantsValue ) {
                if ( arg == null ) {
                    throw new IllegalOptionValueException(this, "");
                }
                return this.parseValue(arg, locale);
            }
            else {
                return Boolean.TRUE;
            }
        }

        /**
         * Override to extract and convert an option value passed on the
         * command-line
         */
        protected Object parseValue( String arg, Locale locale )
            throws IllegalOptionValueException {
            return null;
        }

        private String shortForm = null;
        private String longForm = null;
        private boolean wantsValue = false;

        public static class BooleanOption extends Option {
            public BooleanOption( char shortForm, String longForm ) {
                super(shortForm, longForm, false);
            }
        }

        /**
         * An option that expects an integer value
         */
        public static class IntegerOption extends Option {
            public IntegerOption( char shortForm, String longForm ) {
                super(shortForm, longForm, true);
            }
            protected Object parseValue( String arg, Locale locale )
                throws IllegalOptionValueException {
                try {
                    return new Integer(arg);
                }
                catch (NumberFormatException e) {
                    throw new IllegalOptionValueException(this, arg);
                }
            }
        }

        /**
         * An option that expects a floating-point value
         */
        public static class DoubleOption extends Option {
            public DoubleOption( char shortForm, String longForm ) {
                super(shortForm, longForm, true);
            }
            protected Object parseValue( String arg, Locale locale )
                throws IllegalOptionValueException {
                try {
                    NumberFormat format = NumberFormat.getNumberInstance(locale);
                    Number num = (Number)format.parse(arg);
                    return new Double(num.doubleValue());
                }
                catch (ParseException e) {
                    throw new IllegalOptionValueException(this, arg);
                }
            }
        }

        /**
         * An option that expects a string value
         */
        public static class StringOption extends Option {
            public StringOption( char shortForm, String longForm ) {
                super(shortForm, longForm, true);
            }
            protected Object parseValue( String arg, Locale locale ) {
                return arg;
            }
        }
    }

    /**
     * Add the specified Option to the list of accepted options
     */
    public final Option addOption( Option opt ) {
        this.options.put("-" + opt.shortForm(), opt);
        this.options.put("--" + opt.longForm(), opt);
        return opt;
    }

    /**
     * Convenience method for adding a string option.
     * @return the new Option
     */
    public final Option addStringOption( char shortForm, String longForm ) {
        Option opt = new Option.StringOption(shortForm, longForm);
        addOption(opt);
        return opt;
    }

    /**
     * Convenience method for adding an integer option.
     * @return the new Option
     */
    public final Option addIntegerOption( char shortForm, String longForm ) {
        Option opt = new Option.IntegerOption(shortForm, longForm);
        addOption(opt);
        return opt;
    }

    /**
     * Convenience method for adding a double option.
     * @return the new Option
     */
    public final Option addDoubleOption( char shortForm, String longForm ) {
        Option opt = new Option.DoubleOption(shortForm, longForm);
        addOption(opt);
        return opt;
    }

    /**
     * Convenience method for adding a boolean option.
     * @return the new Option
     */
    public final Option addBooleanOption( char shortForm, String longForm ) {
        Option opt = new Option.BooleanOption(shortForm, longForm);
        addOption(opt);
        return opt;
    }

    /**
     * @return the parsed value of the given Option, or null if the
     * option was not set
     */
    public final Object getOptionValue( Option o ) {
        return values.get(o.longForm());
    }

	public final Object getOptionValue( String longForm ) {
		return values.get(longForm);
	}

	public void printOptions(PrintStream s){
		s.println("Using options: ");
		Iterator keys = values.keySet().iterator();
		while (keys.hasNext()) {
			String longForm = (String) keys.next();
			String value = values.get(longForm).toString();
			s.println(longForm+": "+value);
		}
	}

    /**
     * @return the non-option arguments
     */
    public final String[] getRemainingArgs() {
        return this.remainingArgs;
    }

    /**
     * Extract the options and non-option arguments from the given
     * list of command-line arguments. The default locale is used for
     * parsing options whose values might be locale-specific.
     */
    public final void parse( String[] argv )
        throws IllegalOptionValueException, UnknownOptionException {
        parse(argv, Locale.getDefault());
    }

    /**
     * Extract the options and non-option arguments from the given
     * list of command-line arguments. The specified locale is used for
     * parsing options whose values might be locale-specific.
     */
    public final void parse( String[] argv, Locale locale )
        throws IllegalOptionValueException, UnknownOptionException {
        Vector otherArgs = new Vector();
        int position = 0;
        this.values = new Hashtable(10);
        while ( position < argv.length ) {
            String curArg = argv[position];
            if ( curArg.startsWith("-") ) {
                if ( curArg.equals("--") ) { // end of options
                    position += 1;
                    break;
                }
                String valueArg = null;
                if ( curArg.startsWith("--") ) { // handle --arg=value
                    int equalsPos = curArg.indexOf("=");
                    if ( equalsPos != -1 ) {
                        valueArg = curArg.substring(equalsPos+1);
                        curArg = curArg.substring(0,equalsPos);
                    }
                }
                Option opt = (Option)this.options.get(curArg);
                if ( opt == null ) {
                    throw new UnknownOptionException(curArg);
                }
                Object value = null;
                if ( opt.wantsValue() ) {
                    if ( valueArg == null ) {
                        position += 1;
                        valueArg = null;
                        if ( position < argv.length ) {
                            valueArg = argv[position];
                        }
                    }
                    value = opt.getValue(valueArg, locale);
                }
                else {
                    value = opt.getValue(null, locale);
                }
                this.values.put(opt.longForm(), value);
                position += 1;
            }
            else {
                break;
            }
        }
        for ( ; position < argv.length; ++position ) {
            otherArgs.addElement(argv[position]);
        }

        this.remainingArgs = new String[otherArgs.size()];
        int i = 0;
        for (Enumeration e = otherArgs.elements(); e.hasMoreElements(); ++i) {
            this.remainingArgs[i] = (String)e.nextElement();
        }
    }

    private String[] remainingArgs = null;
    private Hashtable options = new Hashtable(10);
    private Hashtable values = new Hashtable(10);
}
