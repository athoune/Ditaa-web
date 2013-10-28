package Ditaa;

sub strict;
sub warnings;

use File::Temp;

sub new {
    my $class = shift;

    my %args = (@_ % 2) == 0? @_: {};

    return bless {
        _bin_path => $args{bin} || undef,
        _java_path => $args{java} || undef,
    }, $class;
}

# accessors
sub bin_path {
    $_[0]->{_bin_path} = $_[1] if $_[1];
    return shift->{_bin_path};
}

sub java_path {
    $_[0]->{_java_path} = $_[1] if $_[1];
    return shift->{_java_path};
}


# methods
sub render_image {
    my ($self, $input, $output) = @_;

    # error ditaa
    die "error: ditaa binary not found"
        unless (-e $self->bin_path);

    # error java
    die "error: java virtual machine binary not found"
        unless (-e $self->java_path);

    my $filename = $self->_temp_file($input);

    system $self->_make_command($filename, $output); 

    # error image not found
    die "error: image cannot be created" 
        unless (-e $output);
}

sub _temp_file {
    my ($self, $input) = @_;

    my $temp = File::Temp->new(UNLINK => 0);
    print $temp $input;
    $temp->seek(0, SEEK_END);

    return $temp->filename;
}

sub _make_command {
    my ($self, $input, $output) = @_;

    return join ' ', (
        $self->java_path,
        "-jar",
        "'". $self->bin_path ."'",
        "'". $input ."'",
        "'". $output ."'",
    );
}


1;

